OUTPUT_ARCH("riscv")
ENTRY(_start)

MEMORY
{
  ram (rwx) : ORIGIN = 0x80000000, LENGTH = 64K
}

PHDRS
{
  text PT_LOAD FLAGS(5);
  data PT_LOAD FLAGS(6);
}

SECTIONS
{
  . = ORIGIN(ram);

  .text : ALIGN(8)
  {
    *(.text.init)
    *(.text .text.*)
  } > ram :text

  .data : ALIGN(32)
  {
    *(.rodata .rodata.*)
    *(.data .data.*)
    *(.bss .bss.*)
    *(COMMON)
  } > ram :data

  /DISCARD/ :
  {
    *(.note*)
    *(.comment*)
  }
}
