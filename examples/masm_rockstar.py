from rockstar import RockStar

masm_code = """data SEGMENT
  msg DB 'Hello, world.$'
  data ENDS
  code SEGMENT
  ASSUME CS:code,DS:data
  start:
  MOV AX,data
  MOV DS,AX
  lea dx,msg
  mov ah,9h
  int 21h
  MOV AX,4C00h
  INT 21h
  code ENDS
  END start"""
rock_it_bro = RockStar(days=400, file_name='HelloWorld.asm', code=masm_code)
rock_it_bro.make_me_a_rockstar()
