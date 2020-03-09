import pyrtl

i_mem = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name='i_mem')
d_mem = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name='d_mem', asynchronous=True)
rf    = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name='rf', asynchronous=True)
pc = pyrtl.Register(bitwidth=32, name='pc')
branch_step = pyrtl.WireVector(bitwidth=32, name='branch_step')
pc.next <<= pc + 1 + branch_step

#pc.next
instr = pyrtl.WireVector(bitwidth=32, name='instr')
instr <<= i_mem[pc]

rs = pyrtl.WireVector(bitwidth=5, name='rs')
rt = pyrtl.WireVector(bitwidth=5, name='rt')
rd = pyrtl.WireVector(bitwidth=5, name='rd')
func = pyrtl.WireVector(bitwidth=6, name='func')
op = pyrtl.WireVector(bitwidth=6, name='op')
immed = pyrtl.WireVector(bitwidth=16, name='immed')


#ALU input data
data0 = pyrtl.WireVector(bitwidth=32, name='data0')
data1 = pyrtl.WireVector(bitwidth=32, name='data1')

#ALU output data
alu_out = pyrtl.WireVector(bitwidth=32, name='alu_out')

    
#instruction decode logic

rs <<= instr[21:26]
rt <<= instr[16:21]
rd <<= instr[11:16]
func <<= instr[0:6]
op <<= instr[26:32]
immed <<= instr[0:16]
    
r_reg0 = pyrtl.WireVector(bitwidth=5, name='r_reg0')
r_reg1 = pyrtl.WireVector(bitwidth=5, name='r_reg1')
w_data = pyrtl.WireVector(bitwidth=16, name='w_data')
w_reg = pyrtl.WireVector(bitwidth=5, name='w_reg')

reg_dst = pyrtl.WireVector(bitwidth=1, name='reg_dst')
branch = pyrtl.WireVector(bitwidth=1, name='branch')
regwrite = pyrtl.WireVector(bitwidth=1, name='regwrite')
alu_src = pyrtl.WireVector(bitwidth=2, name='alu_src')
mem_write = pyrtl.WireVector(bitwidth=1, name='mem_write')
mem_to_reg = pyrtl.WireVector(bitwidth=1, name='mem_to_reg')
alu_op = pyrtl.WireVector(bitwidth=3, name='alu_op')



#Control logic
with pyrtl.conditional_assignment:
    #R Type
    with op==int(0x00):
        #ADD
        with func==int(0x20):
            reg_dst |= 1
            branch |= 0
            regwrite |= 1
            alu_src |= 0
            mem_write |= 0
            mem_to_reg |= 0
            alu_op |= 0
        #AND
        with func==int(0x24):
            reg_dst |= 1
            branch |= 0
            regwrite |= 1
            alu_src |= 0
            mem_write |= 0
            mem_to_reg |= 0
            alu_op |= 1
        #SLT
        with func==int(0x2a):
            reg_dst |= 1
            branch |= 0
            regwrite |= 1
            alu_src |= 0
            mem_write |= 0
            mem_to_reg |= 0
            alu_op |= 4
    #ADDI
    with op==int(0x8):
        reg_dst |= 0
        branch |= 0
        regwrite |= 1
        alu_src |= 1
        mem_write |= 0
        mem_to_reg |= 0
        alu_op |= 0
    #LUI
    with op==int(0xf):
        reg_dst |= 0
        branch |= 0
        regwrite |= 1
        alu_src |= 1
        mem_write |= 0
        mem_to_reg |= 0
        alu_op |= 2
    #ORI
    with op==int(0xd):
        reg_dst |= 0
        branch |= 0
        regwrite |= 1
        alu_src |= 2
        mem_write |= 0
        mem_to_reg |= 0
        alu_op |= 3
    #LW
    with op==int(0x23):
        reg_dst |= 0
        branch |= 0
        regwrite |= 1
        alu_src |= 1
        mem_write |= 0
        mem_to_reg |= 1
        alu_op |= 0
    #SW
    with op==int(0x2b):
        reg_dst |= 1
        branch |= 0
        regwrite |= 0
        alu_src |= 1
        mem_write |= 1
        mem_to_reg |= 0
        alu_op |= 0
    #BEQ
    with op==int(0x4):
        reg_dst |= 1
        branch |= 1
        regwrite |= 0
        alu_src |= 0
        mem_write |= 0
        mem_to_reg |= 0
        alu_op |= 5


r_reg0 <<= rs
with pyrtl.conditional_assignment:
    with reg_dst==int(0x1):
        r_reg1 |= rt
        w_reg |= rd
    with reg_dst==int(0x0):
        r_reg1 |= rd
        w_reg |= rt


            
#ALU INPUT LOGIC
sign_extended = pyrtl.WireVector(bitwidth=32, name='sign_extended')

zero_msb = 0x0000
one_msb = 0xffff
zero_extended = pyrtl.concat(zero_msb, immed)
one_extended = pyrtl.concat(one_msb, immed)

with pyrtl.conditional_assignment:
    with immed[-1]==int(0x1):
        sign_extended |= one_extended
    with immed[-1]==int(0x0):
        sign_extended |= zero_extended
            
data0 |= rf[r_reg0]
with pyrtl.conditional_assignment:
    with alu_src==int(0x0):
        data1 |= rf[r_reg1]
    with alu_src==int(0x1):
        data1 |= sign_extended
    with alu_src==int(0x2):
        data1 |= zero_extended



eq_check = pyrtl.WireVector(bitwidth=1, name='eq_check')
            
#ALU LOGIC
with pyrtl.conditional_assignment:
    with alu_op==int(0x0):
        alu_out |= data0 + data1
    with alu_op==int(0x1):
        alu_out |= data0 & data1
    with alu_op==int(0x2):
        alu_out |= pyrtl.concat(data0[-16:], zero_msb)
    with alu_op==int(0x3):
        alu_out |= data0 | data1
    with alu_op==int(0x4):
        alu_out |= data0 < data1
    with alu_op==int(0x5):
        eq_check |= data0 == data1
        with eq_check==int(0x1):
            alu_out |= sign_extended
            branch_step |= alu_out
    with alu_op != int(0x5):
        branch_step |= 0x0


#Mem read
with pyrtl.conditional_assignment:
    with mem_to_reg==int(0x1):
        w_data |=  d_mem[alu_out]
    with mem_to_reg==int(0x0):
        w_data |= alu_out
            
#Mem write
with pyrtl.conditional_assignment:
    with mem_write==int(0x1):
        d_mem[alu_out] |= data1
            
#reg write
with pyrtl.conditional_assignment:
    with regwrite==int(0x1):
        rf[w_reg] |= w_data


    
    
    """

    Here is how you can test your code.
    This is very similar to how the autograder will test your code too.

    1. Write a MIPS program. It can do anything as long as it tests the
       instructions you want to test.

    2. Assemble your MIPS program to convert it to machine code. Save
       this machine code to the "i_mem_init.txt" file.
       You do NOT want to use QtSPIM for this because QtSPIM sometimes
       assembles with errors. One assembler you can use is the following:

       https://alanhogan.com/asu/assembler.php

    3. Initialize your i_mem (instruction memory).

    4. Run your simulation for N cycles. Your program may run for an unknown
       number of cycles, so you may want to pick a large number for N so you
       can be sure that the program has "finished" its business logic.

    5. Test the values in the register file and memory to make sure they are
       what you expect them to be.

    6. (Optional) Debug. If your code didn't produce the values you thought
       they should, then you may want to call sim.render_trace() on a small
       number of cycles to see what's wrong. You can also inspect the memory
       and register file after every cycle if you wish.

    Some debugging tips:

        - Make sure your assembly program does what you think it does! You
          might want to run it in a simulator somewhere else (SPIM, etc)
          before debugging your PyRTL code.

        - Test incrementally. If your code doesn't work on the first try,
          test each instruction one at a time.

        - Make use of the render_trace() functionality. You can use this to
          print all named wires and registers, which is extremely helpful
          for knowing when values are wrong.

        - Test only a few cycles at a time. This way, you don't have a huge
          500 cycle trace to go through!


    """


if __name__ == '__main__':
    # Start a simulation trace
    sim_trace = pyrtl.SimulationTrace()

    # Initialize the i_mem with your instructions.
    i_mem_init = {}
    with open('i_mem_init.txt', 'r') as fin:
        i = 0
        for line in fin.readlines():
            i_mem_init[i] = int(line, 16)
            i += 1

    sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={
        i_mem : i_mem_init
    })

    # Run for an arbitrarily large number of cycles.
    for cycle in range(20):
        sim.step({})
    #sim_trace.render_trace()

    # Use render_trace() to debug if your code doesn't work.
    # sim_trace.render_trace()

    # You can also print out the register file or memory like so if you want to debug:
    print(sim.inspect_mem(d_mem))
    print(sim.inspect_mem(rf))

    # Perform some sanity checks to see if your program worked correctly
    #assert(sim.inspect_mem(d_mem)[0] == 10)
    #assert(sim.inspect_mem(rf)[8] == 10)    # $v0 = rf[8]
    #print('Passed!')

    # Perform some sanity checks to see if your program worked correctly
    assert (sim.inspect_mem(rf)[16] == 65536)
    assert (sim.inspect_mem(rf)[17] == 1)
    assert (sim.inspect_mem(rf)[18] == 0)
    assert (sim.inspect_mem(rf)[19] == 5)
    assert (sim.inspect_mem(rf)[20] == 1)
    assert (sim.inspect_mem(rf)[21] == 0xffffffff)
    assert (sim.inspect_mem(d_mem)[0] == 10)
    assert (sim.inspect_mem(rf)[8] == 10)  # $v0 = rf[8]
    print('Passed!')
