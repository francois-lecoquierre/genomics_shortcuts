  
import pandas as pd
import easygui
import matplotlib.pyplot as plt


"""
This script is used to compare the results of the Hap.py tool on different VCF files.
It asks the user to select the files to compare, and then plots the results.
Files are the .stats.csv files generated by Hap.py.

"""


def generate_df(files_list):
    def parse_stats_csv_to_pandas(file):
        df = pd.read_csv(file, sep=",", header=0)
        # add a column for the file name, without the path, and without ".stats.csv"
        df["file"] = file.split("/")[-1]
        # set the file name as the index
        df = df.set_index("file")
        return df
    def parse_stats_xl_to_pandas(file):
        df = pd.read_excel(file, header=0)
        # add a column for the file name, without the path, and without ".stats.csv"
        df["file"] = file.split("/")[-1]
        # set the file name as the index
        df = df.set_index("file")
        return df
    # merge dataframes
    def add_f1_score(df):
        df["f1_score"] = 2 * df["recall"] * df["precision"] / (df["recall"] + df["precision"])
        return df
    df = pd.DataFrame()
    for file in files_list:
        if file.split(".")[-1] == "csv":
            df = df.append(parse_stats_csv_to_pandas(file))
        elif file.split(".")[-1] == "xlsx":
            df = df.append(parse_stats_xl_to_pandas(file))
        else:
            raise ValueError("Extension of the files must be either .csv or .xlsx")
    df = add_f1_score(df)
    return df


def rename_conditions_and_get_a_title(df):
    # this script displays a multenterbox easygui interface that displays the list of files, which the user can rename
    # also asks for the title of the figure
    # returns the df with renamed files, and the title of the figure
    def file_name_auto_formatting(file_name):
        to_remove=[".stats.csv", ".stats.xlsx", "NA12878.", "NA12878_"]
        for element in to_remove:
            file_name = file_name.replace(element, "")
        return file_name
    # create a dict with the default names of the files
    default_figure_title = "NA_12878 comparison"
    renaming_dict={"figure_title": default_figure_title}
    for index in df.index.unique():
        renaming_dict[index] = file_name_auto_formatting(index)
    # create a multenterbox easygui interface
    msg = "Enter a title for the figure and rename the files if necessary (the shorter the better)"
    title = "Rename files"
    field_names = list(renaming_dict.keys())
    field_values = list(renaming_dict.values())
    field_values = easygui.multenterbox(msg, title, field_names, field_values)
    # update the renaming_dict with the new names of the files and the new title of the figure
    for index, value in enumerate(field_values):
        if index == 0:
            renaming_dict["figure_title"] = value
        else:
            renaming_dict[list(renaming_dict.keys())[index]] = value
    # rename the files in the df
    df = df.rename(index=renaming_dict)
    # return the df and the title of the figure
    return df, renaming_dict["figure_title"]
    


def plot_counts(df, figure_title):
    color_dict = {"tp": "#2adf59", "fp": "#f56e85", "fn": "#2a98df"}
    # Fonction pour créer un subplot
    def create_subplot(ax, df, snv_or_indel, interpretation_values, plot_label, display_legend_bool):
        df = df[df["type"] == snv_or_indel][interpretation_values]
        # pour chaque colonne de la dataframe, on fait un barplot empilé
        # on inverse l'ordre des colonnes pour que les barres soient empilées dans le bon ordre
        df = df.iloc[:, ::-1]
        for i, v in enumerate(df.columns):
            # i is the index of the column, v is the name of the column (= the interpretation)
            # on fait un barplot empilé pour chaque colonne
            ax.bar(df.index, df[v], bottom=df.iloc[:, :i].sum(axis=1), label=v, color=color_dict[v])
            # on ajoute le nombre de variants au milieu de chaque sous barre
            for index, value in enumerate(df[v]):
                # calculer la position y pour le texte au milieu de la barre empilée
                y_position = df.iloc[:, :i].sum(axis=1).values[index] + value / 2
                ax.text(index, y_position, str(value), ha="center", va="center")
        if display_legend_bool:
            ax.legend()
        ax.set_title(plot_label)
        ax.set_ylabel("count")
        # background color is light grey
        # ax.set_facecolor("#eaeaf2")
    # Création de la figure et des sous-graphiques, ajout d'un titre et de la légende unique en bas de la figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(figure_title, fontsize=16)
    # Appel de la fonction create_subplot pour chaque sous-graphique
    create_subplot(ax1, df, "SNVs", ["fp"], "SNVs false variants", False)
    create_subplot(ax2, df, "indels", ["fp"], "Indels false variants", False)
    create_subplot(ax3, df, "SNVs", ["fn", "tp"], "SNVs true variants", False)
    create_subplot(ax4, df, "indels", ["fn", "tp"], "Indels true variants", False)
    # ajout de la légende
    legend_elements = [plt.Rectangle((0, 0), 1, 1, color=color_dict["fp"], label="false positives"),
                            plt.Rectangle((0, 0), 1, 1, color=color_dict["tp"], label="true positives"),
                            plt.Rectangle((0, 0), 1, 1, color=color_dict["fn"], label="false negatives")]
    fig.subplots_adjust(bottom=0.2)
    fig.legend(handles=legend_elements, loc='lower center', ncol=3)
    fig.tight_layout(rect=[0, 0.035, 1, 1])
    filename = "counts.png"
    print(f"Saving counts plot : counts.png")
    plt.savefig(filename)


def plot_recall_precision_or_f1_score(df, figure_title, recall_or_precision, color):
    # verify that recall_or_precision is either "recall" or "precision"
    if recall_or_precision not in ["recall", "precision", "f1_score"]:
        raise ValueError("recall_or_precision must be either 'recall', 'precision' or 'f1_score'")
    
    # one plot for snvs, one for indels, and one for both
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(20, 8))
    fig.suptitle(figure_title, fontsize=16)

    for i, snv_or_indel in enumerate(["SNVs", "indels", "records"]):
        # get the dataframe with only snvs or indels
        df_snvs = df[df["type"] == snv_or_indel]
        # plot the recall or precision
        ax = [ax1, ax2, ax3][i]
        ax.bar(df_snvs.index, df_snvs[recall_or_precision], color=color)
        title = (f"{snv_or_indel} {recall_or_precision}").replace("records", "SNVs and indels")
        ax.set_title(title)
        ax.set_ylabel(recall_or_precision)
        # for each plot, add counts at half the height of the bars, with three decimals
        for p in ax.patches:
            ax.annotate(str(round(p.get_height(), 4)), (p.get_x() + p.get_width() / 2, p.get_height()/2), ha='center', va='center')
        # for each plot, add a horizontal line at 1
        ax.axhline(y=1, color="black", linestyle="--")
    
    # save the figure
    print(f"Saving {recall_or_precision} plot : {recall_or_precision}.png")
    plt.savefig(f"{recall_or_precision}.png")



files_list = easygui.fileopenbox(msg="Select the files to compare", title="Select files", multiple=True)
df = generate_df(files_list)
df, experiment_title=rename_conditions_and_get_a_title(df)

plot_counts(df, experiment_title)
plot_recall_precision_or_f1_score(df, experiment_title, "recall", "orange")
plot_recall_precision_or_f1_score(df, experiment_title, "precision", "#a7a6e7")
plot_recall_precision_or_f1_score(df, experiment_title, "f1_score", "#2adf59")



