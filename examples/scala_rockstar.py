from rockstar import RockStar

scala_code = 'object HelloWorld {def main(args: Array[String]) { println("Hello world") }}'
rock_it_bro = RockStar(days=400, file_name='hello.scala', code=scala_code)
rock_it_bro.make_me_a_rockstar()
