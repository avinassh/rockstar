from RockStar import RockStar

csharp_code = """public class helloworld
{
   public static void Main()
   {
      System.Console.WriteLine("Hello, World!");
   }
}"""
rock_it_bro = RockStar(days=400, file_name='helloWorld.cs', code=csharp_code)
rock_it_bro.make_me_a_rockstar()
