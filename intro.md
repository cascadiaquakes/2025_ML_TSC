# 2025 CRESCENT Machine Learning Technical Short Course

## Program Overview
This three-day short course provides a hands-on introduction to machine learning techniques for seismic event analysis. Participants will learn to develop AI-aided earthquake catalogs through three key steps: event detection, association, and location with quality control. The course covers neural network architecture selection, model training, performance metrics, and application to continuous seismic data. The workshop will include a mix of presentations and hands-on tutorials.  The final day will include a participant hack-a-thon in which students attempt to develop a machine learning based quality control workflow to apply to future generations of machine learning earthquake catalogs.

## Learning Goals and Objectives

By the end of this short course, participants will be able to: 

- Explain the role of machine learning in earthquake detection, association, and location. 
- Select appropriate neural network architectures for earthquake detection and phase picking. 
- Train models using labeled seismic datasets and evaluate their performance. 
- Implement trained models to detect and associate seismic events in real-world data. 
- Optimize model parameters for accuracy and efficiency in earthquake cataloging. 
- Integrate machine learning outputs into earthquake location algorithms. 
- Assess model predictions and refine event catalogs through quality control methods. 
- Design end-to-end machine learning workflows tailored to specific seismic networks or research needs. 
- Collaborate on participant-led exercises to improve catalog quality and reliability. 

##  Agenda

| Time             | Day 1 (Mon)                           | Day 2 (Tue)                             | Day 3 (Wed)                              |
|------------------|----------------------------------------|------------------------------------------|-------------------------------------------|
| 8:30 – 9:00am    | Overview Talk: [Intro to AI in Seismology](./slides/slides.pdf) (Marine Denolle) | Research Talk: [Detecting LFEs with a CNN in Cascadia](./slides/lfe_cascadia.pdf) (Amanda Thomas)   | Research Talk: QC Part II (Nate Stevens)       |
| 9:00 – 10:30am   | Research Talk: [AI-ready Data Set for the Pacific Northwest](./slides/ml_pnw_dataset.pdf), [Notebook](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/niyiyu/curated_pnw_dataset_seisbench.html) (Yiyu Ni) | Lecture: [Training a Graph Network](./slides/gnn_introduction.pdf) (Loic Bachelot)            | Research Talk: Catalog Building in the age of AI (Felix Waldhauser)             |
| 10:30 – 11:00am  | Coffee Break                          | Coffee Break | Coffee Break                               |
| 11:00 – 12:30pm  | Lecture: [Training a Phase Picker](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Loic/UNet/make_unet_annotated.html) (Loïc Bachelot) |  Research talk: [Intro to Association](./slides/association.pdf) (Ian McBrearty)  | Hackathon: Event Relocations with HypoDD (Felix Waldhauser)      |
| 12:30 – 1:30pm   | Lunch                                 | Lunch   | Lunch                                      |
| 1:30 – 2:30pm    | Lecture: [More on training a Phase Picker](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Loic/UNet/make_unet_annotated.html)  (Loïc Bachelot)                   		| Research Talk: [Multi-Geohazard Event Discrimination (Akash Kharita)](./slides/discrimination.pdf)                | Participant Lightening Talks and Wrap up     |
| 2:30 – 3:00pm    | Lecture: [Evaluating Model Performance](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Amanda/unet_performance_metrics.html) (Amanda Thomas)                      | Lecture: [Quality Control and Data Wrangling](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Nate/waveform_qc.html) (Nate Stevens)                 |                                           |
| 3:00 – 5:00pm    | Hackathon: [Detect and Pick on continuous Data](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Amanda/apply_unet.html), [Seisbench](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Amanda/seisbench.html), [Pick Database](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Amanda/pickdb.html) (Amanda Thomas)     							| Hackathon: [Quality Control Metrics](https://cascadiaquakes.github.io/2025_ML_TSC/notebooks/Nate/catalog_management.html) (Nate Stevens)     |                                           |


## Prerequisites  

1. Participants must have intermediate python skills including: 

- Core Python Proficiency – Comfortable with syntax, functions, and best practices. 
- Data Handling – Uses pandas and NumPy for data manipulation and analysis. 
- Automation & File Handling – Reads/writes files, automates tasks, and web scrapes with requests. 
- Debugging & Exception Handling – Uses try-except, logging, and debugging tools. 
- Data Visualization – Creates plots using Matplotlib, Seaborn, or plotly. 
- Algorithms & Data Structures – Implements sorting and searching 
- Version Control – Works with Git/GitHub, branches, and pull requests. 
- Python Packages & Environments – Creates/imports modules, manages dependencies with venv/conda.

2. Must have a laptop computer capable of accessing the internet. 


## Instructors

[Marine Denolle](https://denolle-lab.github.io/) (University of Washington)<br>
[Amanda Thomas](https://amtseismo.github.io/) (University of California, Davis)<br>
[Ian McBrearty](https://www.researchgate.net/profile/Ian-Mcbrearty) (Stanford University)<br>
[Loïc Bachelot](https://loicbachelot.github.io/) (University of Oregon)<br>
[Yiyu Ni](https://niyiyu.github.io/) (University of Washington)<br>
[Akash Kharita](https://sites.google.com/view/akashkharita/home) (University of Washington)<br>
[Felix Waldhauser](https://www.ldeo.columbia.edu/~felixw/) (Columbia University)<br>
[Nate Stevens](https://www.researchgate.net/profile/Nathan-Stevens-3) (PNSN | Unversity of Washington)<br>
