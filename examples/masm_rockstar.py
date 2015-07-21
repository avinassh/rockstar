from RockStar import RockStar

masm_code = "data SEGMENT \n msg DB 'Hello, world.$' \n data ENDS \n code SEGMENT \n ASSUME CS:code,DS:data \n start: \n MOV AX,data \n MOV DS,AX \n lea dx,msg \n mov ah,9h \n int 21h \n MOV AX,4C00h \n INT 21h \n code ENDS \n END start"
rock_it_bro = RockStar(days=400, file_name='HelloWorld.asm', code=masm_code)
rock_it_bro.make_me_a_rockstar()
