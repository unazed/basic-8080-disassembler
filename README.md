# unazed-s-basic-8080-disasm
simple PoC disassembler for intel's 8080 isa

requires python 3.8 or further; to backdate to previous versions, reference line 83 (or thereabouts) in `unazed_disasm.py` using  the walrus operator `:=`, a very minor readjustment would be necessary to support the code across most 3.x versions, but i like using it, so it will remain.

usage is simple, `python3 example.py` will invoke the disassembler over the predefined `example.com` 8080 binary, it's fairly simple code, change at ease (the `org` parameter, usually). example output for the given `example.com` yields:

```py
┬─[spectaculum@unazed:/h/d/p/8080_disasm]─[04:49:15 PM]
╰─>$ python example.py
+0          c3  00 7c            JMP (0x007c)         ...  (reloc. -0x100) 
+3          1b                   DCX D                .    
+4          41                   MOV B,C              A    
+5          73                   MOV M,E              s    
+6          73                   MOV M,E              s    
+7          65                   MOV H,L              e    
+8          6d                   MOV L,L              m    
+9          62                   MOV H,D              b    
+a          6c                   MOV L,H              l    
+b          65                   MOV H,L              e    
+c          64                   MOV H,H              d    
+d          20                   *NOP                 .    (unused op.) 
+e          62                   MOV H,D              b    
+f          79                   MOV A,C              y    
+10         20                   *NOP                 .    (unused op.) 
+11         50                   MOV D,B              P    
+12         72                   MOV M,D              r    
+13         65                   MOV H,L              e    
+14         74                   MOV M,H              t    
+15         74                   MOV M,H              t    
+16         79                   MOV A,C              y    
+17         20                   *NOP                 .    (unused op.) 
+18         38                   *NOP                 .    (unused op.) 
+19         30                   *NOP                 .    (unused op.) 
+1a         38                   *NOP                 .    (unused op.) 
+1b         30                   *NOP                 .    (unused op.) 
+1c         20                   *NOP                 .    (unused op.) 
+1d         41                   MOV B,C              A    
+1e         73                   MOV M,E              s    
+1f         73                   MOV M,E              s    
+20         65                   MOV H,L              e    
+21         6d                   MOV L,L              m    
+22         62                   MOV H,D              b    
+23         6c                   MOV L,H              l    
+24         65                   MOV H,L              e    
+25         72                   MOV M,D              r    
+26         0d                   DCR C                .    
+27         0a                   LDAX B               .    
+28         24                   INR H                .    
+29         4c                   MOV C,H              L    
+2a         6f                   MOV L,A              o    
+2b         6e                   MOV L,M              n    
+2c         67                   MOV H,A              g    
+2d         20                   *NOP                 .    (unused op.) 
+2e         62                   MOV H,D              b    
+2f         69                   MOV L,C              i    
+30         6e                   MOV L,M              n    
+31         61                   MOV H,C              a    
+32         72                   MOV M,D              r    
+33         79                   MOV A,C              y    
+34         20                   *NOP                 .    (unused op.) 
+35         69                   MOV L,C              i    
+36         6e                   MOV L,M              n    
+37         69                   MOV L,C              i    
+38         74                   MOV M,H              t    
+39         69                   MOV L,C              i    
+3a         61                   MOV H,C              a    
+3b         6c                   MOV L,H              l    
+3c         69                   MOV L,C              i    
+3d         7a                   MOV A,D              z    
+3e         61                   MOV H,C              a    
+3f         74                   MOV M,H              t    
+40         69                   MOV L,C              i    
+41         6f                   MOV L,A              o    
+42         6e                   MOV L,M              n    
+43         20                   *NOP                 .    (unused op.) 
+44         73                   MOV M,E              s    
+45         65                   MOV H,L              e    
+46         63                   MOV H,E              c    
+47         74                   MOV M,H              t    
+48         69                   MOV L,C              i    
+49         6f                   MOV L,A              o    
+4a         6e                   MOV L,M              n    
+4b         73                   MOV M,E              s    
+4c         20                   *NOP                 .    (unused op.) 
+4d         63                   MOV H,E              c    
+4e         61                   MOV H,C              a    
+4f         6e                   MOV L,M              n    
+50         20                   *NOP                 .    (unused op.) 
+51         62                   MOV H,D              b    
+52         65                   MOV H,L              e    
+53         20                   *NOP                 .    (unused op.) 
+54         64                   MOV H,H              d    
+55         65                   MOV H,L              e    
+56         66                   MOV H,M              f    
+57         69                   MOV L,C              i    
+58         6e                   MOV L,M              n    
+59         65                   MOV H,L              e    
+5a         64                   MOV H,H              d    
+5b         20                   *NOP                 .    (unused op.) 
+5c         75                   MOV M,L              u    
+5d         73                   MOV M,E              s    
+5e         69                   MOV L,C              i    
+5f         6e                   MOV L,M              n    
+60         67                   MOV H,A              g    
+61         20                   *NOP                 .    (unused op.) 
+62         62                   MOV H,D              b    
+63         61                   MOV H,C              a    
+64         73                   MOV M,E              s    
+65         65                   MOV H,L              e    
+66         36  34               MVI M,$0x34          ..   
+68         2d                   DCR L                .    
+69         65                   MOV H,L              e    
+6a         6e                   MOV L,M              n    
+6b         63                   MOV H,E              c    
+6c         6f                   MOV L,A              o    
+6d         64                   MOV H,H              d    
+6e         65                   MOV H,L              e    
+6f         64                   MOV H,H              d    
+70         20                   *NOP                 .    (unused op.) 
+71         73                   MOV M,E              s    
+72         74                   MOV M,H              t    
+73         72                   MOV M,D              r    
+74         69                   MOV L,C              i    
+75         6e                   MOV L,M              n    
+76         67                   MOV H,A              g    
+77         73                   MOV M,E              s    
+78         21  0a 0d            LXI H,$0x0a0d        ...  
+7b         24                   INR H                .    
+7c         11  01 04            LXI D,$0x0104        ...  
+7f         0e  09               MVI C,$0x09          ..   
+81         cd  00 05            CALL (0x0005)        ...  (reloc. out of bounds) 
+84         cd  00 90            CALL (0x0090)        ...  (reloc. -0x100) 
+87         0e  09               MVI C,$0x09          ..   
+89         11  01 29            LXI D,$0x0129        ...  
+8c         cd  00 05            CALL (0x0005)        ...  (reloc. out of bounds) 
+8f         c9                   RET                  .    
+90         3e  21               MVI A,$0x21          ..   
+92         76                   HLT                  v    
+93         3d                   DCR A                .    
+94         c2  00 92            JNZ (0x0092)         ...  (reloc. -0x100) 
+97         c9                   RET        
```

considering it's a fairly simplistic implementation of a disassembler, there is no support for xrefs, string detection, logical chunking, control flow, etc., though it would be fairly simple to implement logical chunking by (optimally adding string detection first) creating a global address table, and adding any in-range addresses into it along the main-loop of `iterate_instructions`. thus you may distinguish different chunks of the code.
