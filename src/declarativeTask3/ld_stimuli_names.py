
supported_languages = ['french', 'english']

picturesNamesEnglish = {
    'a001': 'penguin',
    'a002': 'pig',
    'a003': 'swan',
    'a004': 'squirrel',
    'a005': 'turtle',
    'a006': 'crocodile',
    'a007': 'bear',
    'a008': 'deer',
    'a009': 'dog',
    'a010': 'eagle',
    'a011': 'elephant',
    'a012': 'fish',
    'a013': 'rabbit',
    'a014': 'rhinoceros',
    'a015': 'sheep',
    'a016': 'rooster',
    'a017': 'bird',
    'a018': 'cat',
    'a019': 'duck',
    'a020': 'racoon',
    'a021': 'camel',
    'a022': 'giraffe',
    'a023': 'kangaroo',
    'a024': 'zebra',

    'c001': 'pants',
    'c002': 'shoe',
    'c003': 'skirt',
    'c004': 'sock',
    'c005': 'pullover',
    'c006': 'tie',
    'c007': 'jacket',
    'c008': 'belt',
    'c009': 'dress',
    'c010': 'hat',
    'c011': 'coat',
    'c012': 'mitten',
    'c013': 'necklace',
    'c014': 'glove',
    'c015': 'button',
    'c016': 'purse',
    'c017': 'ribbon',
    'c018': 'watch',
    'c019': 'shirt',
    'c020': 'glasses',
    'c021': 'blouse',
    'c022': 'coat',
    'c023': 'ring',
    'c024': 'boot'
}

picturesNamesFrench = {
    'a001': 'pingouin',
    'a002': 'cochon',
    'a003': 'cygne',
    'a004': 'écureuil',
    'a005': 'tortue',
    'a006': 'crocodile',
    'a007': 'ours',
    'a008': 'cerf',
    'a009': 'chien',
    'a010': 'aigle',
    'a011': 'éléphant',
    'a012': 'poisson',
    'a013': 'lapin',
    'a014': 'rhinocéros',
    'a015': 'mouton',
    'a016': 'coq',
    'a017': 'oiseau',
    'a018': 'chat',
    'a019': 'canard',
    'a020': 'raton laveur',
    'a021': 'chameau',
    'a022': 'girafe',
    'a023': 'kangourou',
    'a024': 'zèbre',

    'c001': 'pantalon',
    'c002': 'chaussure',
    'c003': 'jupe',
    'c004': 'chaussette',  # bas?
    'c005': 'pull',
    'c006': 'cravate',
    'c007': 'veste',
    'c008': 'ceinture',
    'c009': 'robe',
    'c010': 'chapeau',
    'c011': 'veste',
    'c012': 'moufle',
    'c013': 'collier',
    'c014': 'gant',
    'c015': 'bouton',
    'c016': 'sac à main',
    'c017': 'ruban',
    'c018': 'montre',
    'c019': 'chemise',
    'c020': 'lunettes',
    'c021': 'chemisier',
    'c022': 'manteau',
    'c023': 'anneau',
    'c024': 'botte'
}

pictureNames = {'english': picturesNamesEnglish, 'french': picturesNamesFrench}
classNames = {'english': {'a': 'animals', 'c': 'clothes'},
              'french': {'a': 'animaux', 'c': 'vêtements'},
              None: {'a': 'a', 'c': 'c'}}

sound_textbox = {'english': ' Sound: ', 'french': ' Son: '}

# all steps
ttl_instructions_text = {'english': ' PLEASE GET READY ', 'french': ' SOYEZ PRÊTS '}
ending_screen_text = {'english': ' THANK YOU ', 'french': ' MERCI '}

# ld_example.py specific
example_success_feedback_message = {'english': ' PERFECT ', 'french': ' PARFAIT '}
example_failure_feedback_message = {'english': ' GOOD TRY. BUT YOU MISSED SOME... ',
                                    'french': ' BIEN ESSAYÉ. RÉ-ESSAYONS... '}
# ld_GUI_adjust_sound_volumes.py specific
next_sound_text = {'english': ' NEXT SOUND ', 'french': ' PROCHAIN SON '}
ld_GUI_sound_volume_adjustment_end_text = {'english': ' END ', 'french': ' FIN '}
# ld_encoding.py specific
presentation_screen_text = {'english': ' PRESENTATION ', 'french': ' PRÉSENTATION '}
feedback_message = {'english': 'YOUR SCORE', 'french': 'VOTRE SCORE'}
choose_image_text = {'english': ' CHOOSE AN IMAGE ', 'french': ' CHOISISSEZ UNE IMAGE '}
choose_position_text = {'english': ' CHOOSE A LOCATION ', 'french': ' CHOISISSEZ UNE POSITION '}
rest_screen_text = {'english': ' REST ', 'french': ' REPOS '}

# ld_recognition.py specific
correct_location_button_text = {'english': '  CORRECT LOCATION  ', 'french': ' VRAIE POSITION '}
wrong_location_button_text = {'english': '  WRONG LOCATION  ', 'french': ' FAUSSE POSITION '}
