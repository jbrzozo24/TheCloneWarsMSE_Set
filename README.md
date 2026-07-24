# The Clone Wars MTG Set

This is a Magic The Gathering Set that I built based mainly on the The Clone Wars era of Star Wars.
Below, I've listed out some instructions for building the set from my google sheet into MSE and vice versa.


## Set Builder Instructions

``` bash
cd $STEM
git clone git@github.com:jbrzozo24/magic_the_gathering_projects.git
cd magic_the_gathering_projects/src/mse_set_builder_app/
./set_builder.py -v # The defaults are correct already
```

You'll need to set up google_auth in mse_set_builder_app/google_auth, follow the readme in mse_set_builder_app.


## Working with the mse-set file

Run the mse_set_zip.py script to unzip the mse-set and store it in git unzipped.

### Exporting Cards from mse-set files
Open the `set` file.
File > Export > All Card Images > Format = {card.card_code_text}_{card.name}_vX.png (where X is the version number)
Pick a destination foolde

### Creating Nandeck exports

Run the make_nandeck script pointing to the export folder. Omit the cfg file if you want all files generated.
This will create a text file. Open nanDECK and paste the contents of the text file in. Run Validate. Run Build Deck (replace the generated text file, it is the same text we generated).
Run print deck, this gets the cards out in PDF form. Save the PDF. Then print it at 97% size.
