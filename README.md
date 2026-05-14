# Trends in Microwaves, Optoelectronics and Electromagnetics: A Bibliometric Analysis of JMOe (2010–2025)

## About the paper

This paper was submitted to the *Journal of Microwaves, Optoelectronics and Electromagnetic Applications* (JMOe) in 2026. This work presents a bibliometric and scientometric analysis of JMOe from 2010 to 2025, characterizing its development, impact, and research structure through quantitative methods including co-authorship network analysis, gender inference, and topic modeling via BERTopic with LLM-assisted semantic labeling.

## Authors (original paper)

| Author | Affiliation |
|---|---|
| Hevila S. de Freitas | UEMA, Brazil |
| Gabriele de S. Araújo | UEMA, Brazil |
| Gustavo S. Silva | UEMA, Brazil |
| Fábio M. F. Lobato | UFOPA, Brazil |
| Antonio F. L. Jacob Jr. | UEMA, Brazil |

**Center for Technological Sciences — State University of Maranhão (UEMA)**, São Luís, MA, Brazil.

**Institute of Engineering and Geosciences — Federal University of Western Pará (UFOPA)**, Santarém, Pará, Brazil.

## Abstract

The rapid growth of scientific output highlights the importance of systematically assessing specialized journals, particularly in fields central to communications infrastructure. Although the *Journal of Microwaves, Optoelectronics and Electromagnetic Applications* (JMOe) is a leading Brazilian journal in these areas, it lacks longitudinal studies examining its thematic evolution and collaboration patterns. This work presents a bibliometric and scientometric analysis of JMOe from 2010 to 2025 to characterize its development, impact, and research structure. Adopting a quantitative approach, the study utilized metadata from SciELO and citation data from Google Scholar. The methodology involves authorship normalization, gender inference using a multi-step protocol and manual validation, co-authorship network analysis, and topic modeling via BERTopic, with semantic labeling supported by Large Language Models (LLMs). The results identify the most productive authors, institutions, and countries, indicating the consolidation of research topics such as microstrip antennas and 5G technologies. The findings also reveal a persistent gender imbalance in the field. Overall, this study provides a structured overview of JMOe's directions and scientific trajectory over the last 15 years, offering valuable insights into the journal's role within the global and regional scientific community.


## Citation

If you use any of the resources available here, please cite our work:


> Freitas, H., Araújo, G., Silva, G., Lobato, F., & Jacob Jr., A. (2025). Trends in Microwaves, Optoelectronics and Electromagnetics: A Bibliometric Analysis of JMOe (2010–2025). *Journal of Microwaves, Optoelectronics and Electromagnetic Applications*.

## BibTeX

```bibtex
@article{freitas2026jmoe,
  title={Trends in Microwaves, Optoelectronics and Electromagnetics: A Bibliometric Analysis of JMOe (2010--2025)},
  author={Freitas, Hevila S. de and Ara{\'u}jo, Gabriele de S. and Silva, Gustavo S. and Lobato, F{\'a}bio M. F. and Jacob Jr., Antonio F. L.},
  journal={Journal of Microwaves, Optoelectronics and Electromagnetic Applications},
  year={2026}
}
```

---

## Directory description

```
/
├── src/                   ← source code used to generate the analyses presented in the paper
│   ├── 01_scielo_crawler.ipynb              ← collects article metadata from SciELO
│   ├── 02_extrair_citacoes_googlescholar.ipynb  ← retrieves citation counts via Google Scholar
│   ├── 03_pp_vosviewer.ipynb                ← preprocesses data for VOSviewer; geographic analysis
│   ├── 04_autores_jmoe.ipynb                ← author normalization, gender inference and analysis
│   └── 05_topic_modelling_jmoe.ipynb             ← BERTopic pipeline with LLM-assisted topic labeling
│
│
├── figures/               ← figures used in the paper, including supplementary figures
│
├── data/             ← original and preprocessed CSV files used in the analyses
```

---

## Source code overview

| Script | Description |
|---|---|
| `01_scielo_crawler.ipynb` | Web crawler that collects article metadata (title, authors, abstract, keywords, references) from SciELO editions of JMOe and stores them in MongoDB. |
| `02_extrair_citacoes_googlescholar.ipynb` | Queries Google Scholar via ScraperAPI to retrieve citation counts for each article. Supports checkpoint-based resumption of interrupted runs. |
| `03_pp_vosviewer.ipynb` | Cleans and standardizes author names, affiliations, and keywords; normalizes plurals and country names; exports a VOSviewer-ready CSV; generates a choropleth world map and a Top 10 countries bar chart. |
| `04_autores_jmoe.ipynb` | Expands author lists per article, normalizes names (accent removal, abbreviation expansion), infers gender via the IBGE API, applies a manual unification map, and produces a gender distribution chart. |
| `05_topic_modelling.ipynb` | Full BERTopic pipeline: text preprocessing with spaCy, semantic embeddings (all-mpnet-base-v2), HDBSCAN clustering, LLM-assisted topic labeling (DeepSeek / Gemma), UMAP visualizations, temporal heatmaps, and word clouds. |

---

## Requirements

All scripts were developed and tested in **Google Colab** with Python 3.10+.

```bash
pip install pandas requests beautifulsoup4 unidecode loguru pymongo \
            requests-html bertopic sentence-transformers nltk spacy \
            hdbscan umap-learn transformers accelerate plotly kaleido \
            seaborn datamapplot wordcloud colorcet scikit-learn
python -m spacy download en_core_web_sm
```

> **Note:** `01_scielo_crawler.py` requires a local MongoDB instance.  
> `02_extrair_citacoes_googlescholar.py` requires a [ScraperAPI](https://www.scraperapi.com/) key.  
> `05_topic_modelling_jmoe.ipynb` requires a [HuggingFace](https://huggingface.co/) token to download the LLM models.

## Data availability

The raw and preprocessed CSV files used in all analyses are available in the `data/` directory. The original metadata was collected from [SciELO](https://www.scielo.br/j/jmoea/) and citation counts from Google Scholar.
