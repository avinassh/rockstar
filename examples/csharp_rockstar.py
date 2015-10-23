from rockstar import RockStar

csharp_code = """using System;

class HelloWorld
{
    static void Main()
    {
        Console.WriteLine("Hello world");
    }
}"""
rock_it_bro = RockStar(days=400, file_name='helloWorld.cs', code=csharp_code)
rock_it_bro.make_me_a_rockstar()
