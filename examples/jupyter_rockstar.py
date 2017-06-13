from rockstar import RockStar

jupyter_code = """
'text': [
  'Hello, world!'
]
"""

rock_it_bro = RockStar(days=400, file_name='helloworld.ipynb', code=jupyter_code)
rock_it_bro.make_me_a_rockstar()
