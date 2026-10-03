#ifndef FDI_TEST_COMMON_H
#define FDI_TEST_COMMON_H
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint64_t word_t;
typedef uint64_t vaddr_t;
#define Assert(condition, ...) assert(condition)
#define MUXDEF(config, yes, no) yes
#define MODE_M 3
#define MODE_S 1
#define MODE_U 0
#endif
