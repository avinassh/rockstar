from rockstar import RockStar

mmix_code = """LOC	Data_Segment
	GREG	@
txt	BYTE	"Hello world!",10,0

	LOC	#100
	
Main	LDA	$255,txt
	TRAP	0,Fputs,StdOut
	TRAP	0,Halt,0
"""

rock_it_bro = RockStar(days=400, file_name='helloWorld.mms', code=mmix_code)
rock_it_bro.make_me_a_rockstar()
