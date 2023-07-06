## Description (English)

What is this project?

This project involves the development of an open-source propagation model that predicts the RF path loss in foliage dominant environments. The motivation for the work was the recognition that commercially available propagation tools were not able to provide sufficiently accurate predictions in these types of environments. This is largely due to the lack of sufficient local information in these commercial tools, an inadequacy that this project hopes to remedy.

How does it work?

This source code begins with a very solid open-source propagation model, namely P.1812-6 [1], developed by the ITU. On its own, this propagation model provides acceptable performance in terms of path loss prediction accuracy. We also make use of openly available high resolution terrain and surface information databases, which further improves the prediction accuracy of the technique. We have additionally included more accurate foliage loss models (through and diffracted components - based on references [2] to [4]) that can help improve the path loss prediction accuracy when communication links are dominated by foliage blockage.

Who will use this project?

Any individual or team interested in obtaining accurate path loss estimates in foliage dominated environments.

What is the goal of this project?

The goal of this project is to provide Canadian businesses, academics and the general public open access to modern propagation models, specifically targeting foliage dominated communications environments.

## Description (Français)

Quel est ce projet ?

Ce projet se concentre sur le développement d’un modèle de propagation libre d'accès ("open source") qui prédit l'affaiblissement de propagation pour les systèmes hertziens terrestres dans des zones rurales avec une végétation abondante. La motivation derrière ces travaux était de reconnaître que les logiciels de propagation commerciaux disponibles aujourd'hui ne sont pas en mesure de fournir des estimés suffisamment précis dans ces types d’environnements. Ceci est dû en grande partie au manque d’informations précises sur les obstacles nuisant à la propagation sur ces liens radio; ce projet tente d'y remédier.


Comment cela fonctionne-t-il ?

Ce code source utilise tout d'abord un modèle de propagation libre d'accès reconnu, la recommendation P.1812-6 [1], développée par l'UIT. À lui seul, ce modèle de propagation offre des performances acceptables. Nous utilisons également des données libres d'accès de haute résolution du terrain et des groupes d'obstacles à la surface de la Terre, ce qui améliore encore la précision de la prédiction des affaiblissements du signal. Nous avons également ajouté des modèles précis d'affaiblissement dû à la végétation (les composantes de diffusion à travers la végétation ainsi que celles par diffraction sur la couverture végétale) basés sur les références [2] à [4]) qui peuvent aider à améliorer la précision des estimés en milieu rural avec une végétation abondante.


Qui utilisera ce projet?

Toute personne ou équipe intéressée à obtenir des estimations précises de l'affaiblissement de propagation pour les systèmes terrestres dans des zones rurales avec une végétation abondante.



Quel est l’objectif de ce projet?

L’objectif de ce projet est de fournir aux entreprises, aux universités et au grand public canadiens un accès libre aux modèles de propagation modernes, ciblant spécifiquement les environnements ruraux avec une végétation abondante.


## Installation

Using Conda , you can install all the librairies needed for the project at once using this command : 
```
cd SAFE-tool
conda create --name SAFE --file requirements.txt -c conda-forge
conda activate SAFE
```

You also need wget, as it can't be installed automatically : 
```
pip install wget
```

After installation, you can run the SAFE tool by running main.py.
```
python main.py
```

All the downloads needed are made within the script. 

## References / Références

[1] P.1812 : A path-specific propagation prediction method for point-to-area terrestrial services in the frequency range 30 MHz to 6 000 MHz (https://www.itu.int/rec/R-REC-P.1812-6-202109-I/en)

[2] R. A. Johnson and F. Schwering, “A transport theory of millimeter-wave propagation in woods and forests,” U.S. Army CECOM, Fort Monmouth, NJ, R&D Tech. Rep. CECOM-TR-85-1, Feb. 1985.

[3] J. H. Whitteker, "A generalized solution for diffraction over a uniform array of absorbing half screens," IEEE Trans. Antennas Propag., vol. 49, no. 6, pp. 934-938, June 2001.

[4] P.833 : Attenuation in vegetation (https://www.itu.int/rec/R-REC-P.833-10-202109-I/en)

## Citation

If you find this work useful, please cite it as:
```
@article{ha2022SAFETool,
  title   = "SAFE tool",
  author  = "Chateauvert, Mathieu, Ethier, Jonathan and Bouchard, Pierre",
  year    = "2022",
  publisher = "Communication Research Centre, Canada",
  url     = "https://github.com/ic-crc/SAFE-Tool”
}
```
