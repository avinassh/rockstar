from rockstar import RockStar

eiffel_code = """class
    HELLO_WORLD
create
    make
feature
    make
        do
            print ("Hello, world!%N")
        end
    end
"""

rock_it_bro = RockStar(days=400, file_name='helloworld.e', code=eiffel_code)
rock_it_bro.make_me_a_rockstar()
