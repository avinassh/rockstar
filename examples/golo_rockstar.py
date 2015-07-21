
from rockstar import RockStar

golo_code = """"module hello.world

function main = |args| { 
  println('Hello world')
}"""
rock_it_bro = RockStar(days=400, file_name='golo.golo', code=golo_code)
rock_it_bro.make_me_a_rockstar()
