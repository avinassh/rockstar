from rockstar import RockStar

ada_code = """with Ada.Text_IO;

procedure Hello_World is
use Ada.Text_IO;
begin
  Put_Line("Hello, world!");
end;"""

rock_it_bro = RockStar(days=400, file_name='helloworld.ada', code=ada_code)
rock_it_bro.make_me_a_rockstar()
