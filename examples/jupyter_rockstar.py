from rockstar import RockStar

jupyter_code = """
{
	"cells": [{
		"cell_type": "markdown",
		"metadata": {},
		"source": [
			"# Hello, world!"
		]
	}]
}
"""

rock_it_bro = RockStar(days=100, file_name='helloworld.ipynb', code=jupyter_code)
rock_it_bro.make_me_a_rockstar()
