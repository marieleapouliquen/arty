# Portfolio artistique (Jekyll / GitHub Pages)

Site-portfolio d'inspiration « Order » (Format) : colonne de navigation fixe à gauche, œuvres en grille, visionneuse plein écran, page d'actualités en fil vertical. Aucune dépendance hors des plugins autorisés par GitHub Pages ; pas de framework JS.

## Arborescence

```
_config.yml              réglages : nom, adresse, liens, options d'images
_data/navigation.yml     menu de gauche (rubriques et liens)
_galleries/*.md          une rubrique = un fichier (liste des œuvres dans le front matter)
_posts/*.md              actualités (page d'accueil)
a-propos.md              page de présentation
assets/img/works/full/   grands formats (visionneuse)
assets/img/works/thumbs/ vignettes (grilles)
assets/img/news/         images des actualités
assets/css/main.css      toute la mise en forme (variables en tête de fichier)
assets/js/main.js        menu mobile, visionneuse, protection légère
tools/prepare_images.py  redimensionnement, nettoyage EXIF, signature, YAML prêt à coller
```

## Mise en ligne

1. Créer un nouveau dépôt public sur GitHub (ex. `arty`), y déposer le contenu de ce dossier.
2. **Settings → Pages** : *Deploy from a branch*, branche `main`, dossier `/ (root)`.
3. Ajuster l'adresse dans `_config.yml` (`url` et `baseurl`), selon l'un des deux cas ci-dessous.

### Cas A : sous-chemin du domaine existant

Comme le dépôt utilisateur `marieleapouliquen.github.io` porte déjà le domaine `www.marieleapouliquen.com`, tout dépôt de projet est servi automatiquement sous ce domaine :
`https://www.marieleapouliquen.com/<nom-du-dépôt>/`.

```yaml
url: "https://www.marieleapouliquen.com"
baseurl: "/arty"      # = nom exact du dépôt
```

Attention : si le dépôt s'appelle `art`, il entrera en concurrence avec le dossier `/art` actuellement publié par le site académique. Choisir un autre nom, ou retirer d'abord ce dossier du dépôt académique (en prévoyant une redirection).

### Cas B : domaine dédié (ex. `www.mlykscorner.fr`)

1. Créer à la racine un fichier `CNAME` contenant une seule ligne : `www.mlykscorner.fr`
2. `_config.yml` : `url: "https://www.mlykscorner.fr"` et `baseurl: ""`
3. Zone DNS chez OVH (même schéma que pour le site académique) :
   - apex `mlykscorner.fr` : quatre enregistrements A vers `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `www` : CNAME vers `marieleapouliquen.github.io.`
4. Settings → Pages : renseigner le domaine, attendre la vérification, puis cocher *Enforce HTTPS*.

## Ajouter des œuvres

```bash
pip install Pillow
# placer les photos originales dans sources/<rubrique>/ (dossier ignoré par git)
python tools/prepare_images.py sources/d-apres-nature --watermark "© M.-L. Pouliquen"
```

Le script écrit grands formats et vignettes, supprime les métadonnées (GPS compris) et imprime des lignes à coller sous `works:` dans `_galleries/d-apres-nature.md` :

```yaml
  - file: lavis-maree-basse.jpg
    title: Lavis, marée basse
    year: 2025
    medium: encre sur papier
    dimensions: 30 × 40 cm        # facultatif
    note: d'après une photographie de …   # facultatif (utile pour « études »)
    alt: Paysage à l'encre, …     # facultatif ; par défaut = titre
    width: 900
    height: 675
```

L'ordre de la liste est l'ordre d'affichage. Les images `exemple-*.jpg` sont des gabarits à supprimer.

## Options d'une rubrique (front matter)

| clé | valeurs | effet |
|---|---|---|
| `display` | `grid` · `rows` · `stack` | colonnes en quinconce · lignes justifiées (exige `width`/`height`) · une œuvre par ligne |
| `captions` | `true` / `false` | légende sous chaque vignette, ou seulement dans la visionneuse |
| `show_title` | `true` / `false` | titre de la rubrique au-dessus de la grille |
| `image` | chemin | image de partage (réseaux sociaux) |

Texte sous le front matter = introduction facultative au-dessus de la grille.

**Nouvelle rubrique** : copier un fichier de `_galleries/` (le nom du fichier devient l'URL), puis ajouter le lien dans `_data/navigation.yml`.

## Actualités

Un fichier `_posts/AAAA-MM-JJ-titre.md` par entrée, avec `title`, `venue` (lieu et dates) et `image` facultative. Les plus récentes en haut. S'il n'y a pas d'actualités, on peut faire d'une rubrique la page d'accueil : remplacer `index.md` par une copie de rubrique avec `permalink: /`, et retirer le lien « actualités » du menu.

## Tester en local

```bash
bundle install
bundle exec jekyll serve      # http://127.0.0.1:4000/<baseurl>/
```

## Personnaliser

Couleurs, police, largeur de colonne et espacements : variables `:root` en tête de `assets/css/main.css`. La police (Instrument Sans, Google Fonts) se change dans `_includes/head.html` et `--font`.

## Limites

- La protection des images (clic droit, glisser-déposer) n'est que dissuasive ; la seule vraie protection est de publier des fichiers de résolution modeste, éventuellement signés.
- `noai, noimageai` est une demande adressée aux robots d'indexation, pas une interdiction technique.
