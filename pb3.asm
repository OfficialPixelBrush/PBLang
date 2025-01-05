#once
#bankdef b4
{
    #addr 0x00
    #addr_end 0xff
    #outp 8 * 0x00
	#bits 8
}

#ruledef
{
    ldi {imm: s5}       => imm  @ 0b000
    st {addr: u5}       => addr @ 0b001
    ld {addr: u5}       => addr @ 0b010
    add {addr: u5}      => addr @ 0b011
    xnor {addr: u5}     => addr @ 0b100
    jpnc {addr: s5}      => {
        reladdr = addr - $
        reladdr`5 @ 0b101
    }
    jpz {addr: s5}      => {
        reladdr = addr - $
        reladdr`5 @ 0b110
    }
    hlt                 => 0x07
}
