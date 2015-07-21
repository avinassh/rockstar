from rockstar import RockStar

pascal_code = """program HelloWorld;

  begin
	writeln('Hello World');
  end."""

rock_it_bro = RockStar(days=400, file_name='helloworld.pas', code=pascal_code)
rock_it_bro.make_me_a_rockstar()
