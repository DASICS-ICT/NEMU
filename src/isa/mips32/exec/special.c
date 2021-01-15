#include <cpu/exec.h>

def_EHelper(inv) {
  rtl_hostcall(s, HOSTCALL_INV, NULL, NULL, NULL, 0);
  print_asm("invalid opcode");
}

def_EHelper(nemu_trap) {
  rtl_hostcall(s, HOSTCALL_EXIT, NULL, &cpu.gpr[2]._32, NULL, 0); // gpr[2] is $v0
  print_asm("nemu trap");
}
