from rockstar import RockStar

plsql_code = """CONN scott/tiger
SET SERVEROUTPUT ON 
BEGIN
DBMS_OUTPUT.PUT_LINE('Hello World') ;
END;"""
rock_it_bro = RockStar(days=400, file_name='helloWorld.sql', code=plsql_code)
rock_it_bro.make_me_a_rockstar()
