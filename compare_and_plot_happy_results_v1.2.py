
import pandas as pd
import easygui
import matplotlib.pyplot as plt


def generate_df(files_list):
    def parse_stats_csv_to_pandas(file):
        df = pd.read_csv(file, sep=",", header=0)
        # add a column for the file name, without the path, and without ".stats.csv"
        df["file"] = file.split("/")[-1]
        df = format_name(df)
        # set the file name as the index
        df = df.set_index("file")
        return df
    def parse_stats_xl_to_pandas(file):
        df = pd.read_excel(file, header=0)
        # add a column for the file name, without the path, and without ".stats.csv"
        df["file"] = file.split("/")[-1]
        df = format_name(df)
        # set the file name as the index
        df = df.set_index("file")
        return df
    def format_name(df):
        # remove unwanted parts of the name, stored in the "file" column
        to_remove=[".stats.csv", ".stats.xlsx", "NA12878.", "NA12878_", "01"]
        for part in to_remove:
            df["file"] = df["file"].str.replace(part, "")
        return df
    # merge dataframes
    df = pd.DataFrame()
    for file in files_list:
        if file.split(".")[-1] == "csv":
            df = df.append(parse_stats_csv_to_pandas(file))
        elif file.split(".")[-1] == "xlsx":
            df = df.append(parse_stats_xl_to_pandas(file))
        else:
            raise ValueError("Extension of the files must be either .csv or .xlsx")
    return df



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


def plot_recall_or_precision(df, figure_title, recall_or_precision, color):
    # verify that recall_or_precision is either "recall" or "precision"
    if recall_or_precision not in ["recall", "precision"]:
        raise ValueError("recall_or_precision must be either 'recall' or 'precision'")
    
    # one plot for snvs, one for indels
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(13, 8))
    fig.suptitle(figure_title, fontsize=16)

    for i, snv_or_indel in enumerate(["SNVs", "indels"]):
        # get the dataframe with only snvs or indels
        df_snvs = df[df["type"] == snv_or_indel]
        # plot the recall or precision
        ax = [ax1, ax2][i]
        ax.bar(df_snvs.index, df_snvs[recall_or_precision], color=color)
        ax.set_title(f"{snv_or_indel} {recall_or_precision}")
        ax.set_ylabel(recall_or_precision)
        # for each plot, add counts at half the height of the bars, with three decimals
        for p in ax.patches:
            ax.annotate(str(round(p.get_height(), 4)), (p.get_x() + p.get_width() / 2, p.get_height()/2), ha='center', va='center')
        # for each plot, add a horizontal line at 1
        ax.axhline(y=1, color="black", linestyle="--")
    
    # save the figure
    print(f"Saving {recall_or_precision} plot : {recall_or_precision}.png")
    plt.savefig(f"{recall_or_precision}.png")





files_list = easygui.fileopenbox(msg="Select the files to compare", title="Select files", default="/home/adm-loc/Documents/Programmes/python/data_happy/results_onco/", multiple=True)
experiment_title = easygui.enterbox(msg="Enter the title of the figure", title="Figure title", default="Comparison of the results of the variant calling pipelines")

df = generate_df(files_list)
plot_counts(df, experiment_title)
plot_recall_or_precision(df, experiment_title, "recall", "orange")
plot_recall_or_precision(df, experiment_title, "precision", "#a7a6e7")



