from rockstar import RockStar

d_code = """import std.stdio;

void main()
{
  writeln("Hello, world!");
}"""

rock_it_bro = RockStar(days=400, file_name='helloworld.d', code=d_code)
rock_it_bro.make_me_a_rockstar()
