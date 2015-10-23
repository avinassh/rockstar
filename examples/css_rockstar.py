from rockstar import RockStar

css_code = """body:before {
  content: "Hello, world!";
}"""

rock_it_bro = RockStar(days=400, file_name='helloworld.css', code=css_code)
rock_it_bro.make_me_a_rockstar()
