BUILD_DIR ?= /tmp/nemu-dasics-semantics
RISCV_CC ?= riscv64-linux-gnu-gcc
RISCV_OBJCOPY ?= riscv64-linux-gnu-objcopy
RISCV_NM ?= riscv64-linux-gnu-nm
PYTHON ?= python3
NEMU_CONFIG ?= $(abspath $(dir $(NEMU_SO))/../.config)

ELF := $(BUILD_DIR)/dasics-semantics.elf
BIN := $(BUILD_DIR)/dasics-semantics.bin
OBJ := $(BUILD_DIR)/dasics-semantics.o

.PHONY: check diagnostic

check: $(BIN)
	@test -n "$(NEMU_SO)" || { echo "NEMU_SO must name a DASICS reference shared object" >&2; exit 2; }
	@test -n "$(NEMU_SO_SHA256)" || { echo "NEMU_SO_SHA256 must bind the trusted reference artifact" >&2; exit 2; }
	$(PYTHON) run_semantics.py --so "$(NEMU_SO)" --so-sha256 "$(NEMU_SO_SHA256)" --config "$(NEMU_CONFIG)" --elf "$(ELF)" --bin "$(BIN)" --nm "$(RISCV_NM)"

diagnostic: $(BIN)
	@test -n "$(NEMU_SO)" || { echo "NEMU_SO must name a DASICS reference shared object" >&2; exit 2; }
	@test -n "$(NEMU_SO_SHA256)" || { echo "NEMU_SO_SHA256 must bind the trusted reference artifact" >&2; exit 2; }
	$(PYTHON) run_semantics.py --diagnostic --so "$(NEMU_SO)" --so-sha256 "$(NEMU_SO_SHA256)" --config "$(NEMU_CONFIG)" --elf "$(ELF)" --bin "$(BIN)" --nm "$(RISCV_NM)"

$(OBJ): semantic_runtime.S
	@mkdir -p "$(BUILD_DIR)"
	$(RISCV_CC) \
		-c \
		-nostdlib \
		-fno-pic \
		-fno-pie \
		-march=rv64imac_zicsr \
		-mabi=lp64 \
		semantic_runtime.S \
		-o "$@"

$(ELF): $(OBJ) linker.ld
	$(RISCV_CC) \
		-nostdlib \
		-static \
		-no-pie \
		-Wl,--build-id=none \
		-Wl,--no-relax \
		-Wl,-T,linker.ld \
		"$(OBJ)" \
		-o "$@"

$(BIN): $(ELF)
	$(RISCV_OBJCOPY) -O binary "$<" "$@"
