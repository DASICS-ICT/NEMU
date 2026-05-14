# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库定位

本仓库是 **OpenXiangShan/NEMU 的 DASICS 分叉**，由 DASICS-ICT 团队维护，用于：

1. **作为 XiangShan / NutShell / 香山南湖系列处理器的 difftest reference**（编译为 `.so` 共享库供 RTL 仿真器调用）
2. **DASICS 硬件安全扩展的参考实现**（Library/Jump Bounds、`dasicscall.j/jr`、用户/超级用户检查异常）
3. **SPEC CPU 用 SimPoint checkpoint 工具**（与 spec-playground 的 SPEC 编译流水线对接）
4. 独立解释器，启动 baremetal 程序、bbl、OpenSBI + Linux

当前默认分支是 `dasics-master`；与上游 OpenXiangShan/NEMU 不同步，**不要把 `master` 当作主线**。`include/config/auto.conf` 是 `make <name>_defconfig` 自动生成的，不要手动编辑。

## 必备环境

- **`NEMU_HOME` 必须指向仓库根**。Makefile 第 17–19 行直接 `error` 检查，没设就编不动。
- 第一次构建必须先 `make <某个>_defconfig`，否则 `.config` 不存在会报红字告警（见 `scripts/config.mk:19`）。
- `ready-to-run` 是 git 子模块（指向 Gitee `dasics/ready-to-run` 的 `dev-nemu-difftest` 分支），存放预编译 bbl/Linux/coremark 镜像，需要时手动 `git submodule update --init ready-to-run`。
- softfloat 是 build 时按需 clone 的（`resource/softfloat/repo/`），首次编 `CONFIG_FPU_SOFT` 会自动拉 `ucb-bar/berkeley-softfloat-3`。

## 构建流程的三种"形态"

NEMU 的 `<isa>-nemu-interpreter` 二进制有三种产物形态，配置上互斥，后续命令也不一样：

| 形态 | 触发开关 | 产物 | 用途 |
|------|---------|------|------|
| **独立解释器** | 默认 | `build/<isa>-nemu-interpreter` | 加 `-b` 跑镜像；可作 checkpoint 工具 |
| **difftest reference (共享库)** | `CONFIG_SHARE=y`（`*-ref_defconfig`） | `build/<isa>-nemu-interpreter-so` | RTL 仿真器 `dlopen` 用，禁用 readline/SDL2/`PERF_OPT` |
| **dual-ref**（两个 NEMU 互相 difftest） | `riscv64-dual-xs-ref_defconfig` | 同时是 dut 和 ref | 验证 NEMU 自身一致性 |

`CONFIG_SHARE` 与 `CONFIG_DIFFTEST` **互斥**——前者把自己变成被引用的 ref，后者是把别人当 ref 调起来 difftest。

## defconfig 命名约定

`configs/` 下每个文件代表一种处理器/场景配置：

- `xs-*`：XiangShan（南湖 V2）默认配置
- `nutshell-*`：NutShell（南湖 V2 之前的教学处理器）
- `southlake-*`：香山南湖 V3a（南湖系列第三代）
- `dasics-*`：开启 `CONFIG_RV_DASICS`，含 DASICS CSR、`dasicscall.*` 指令、`EX_DUCF`/`EX_DSCF` 异常
- `*-ref-*`：作 difftest 共享库使用，`CONFIG_SHARE=y` + `CONFIG_PERF_OPT=n`
- `*-fpga-*`：FPGA 部署相关，UART/外设地址不同
- `*-debug-*`：开 `CONFIG_DEBUG`、关 `CONFIG_PERF_OPT`，以便单步/反汇编日志（性能掉一个数量级）

## 常用命令

```bash
export NEMU_HOME=$(pwd)

# 配置 + 编译
make riscv64-xs_defconfig                # 选 XiangShan 默认配置
make menuconfig                          # 交互式调整
make -j                                  # 编译，产物 build/riscv64-nemu-interpreter

# 启动镜像（baremetal / bbl）
./build/riscv64-nemu-interpreter -b ready-to-run/coremark-2-iteration.bin
./build/riscv64-nemu-interpreter -b ready-to-run/linux.bin

# 取 SimPoint 均匀 checkpoint（用 SPEC 时常见）
./build/riscv64-nemu-interpreter \
    --cpt-interval 10000000 -u -b \
    -D output_top -C test -w linux \
    -r ./resource/gcpt_restore/build/gcpt.bin \
    --dont-skip-boot \
    -I 11000000 ./ready-to-run/linux-0xa0000.bin

# 恢复 checkpoint
./build/riscv64-nemu-interpreter -b --restore output_top/test/linux/0/_10000003_.gz

# 跑 cpu-tests 全测（依赖外部 abstract-machine 仓库 ../am-kernels）
bash scripts/runall.sh ISA=riscv64

# 编译为 difftest reference 共享库
make riscv64-xs-ref_defconfig && make -j
# 产物：build/riscv64-nemu-interpreter-so

# clean
make clean       # 清编译产物，保留 .config
make distclean   # 同时清 .config 和 generated/
make clean-all   # 加上 softfloat、tools/ 全清
```

## 代码架构核心

### 顶层执行循环（`src/cpu/cpu-exec.c`）

主入口 `engine_start()` → `execute(n)`。两条路径：

- **`CONFIG_PERF_OPT=y`（独立解释器默认开）**：使用 **trace cache (`tcache`)** + **basic block 链接** + **computed goto 跳转表**。指令分发通过 `goto *(s->EHelper)` 直跳到 `def_EHelper(name) { ... }` 的标签。`end_of_bb`/`end_of_loop` 是关键控制流锚点。新加指令时若涉及非顺序控制流（jr、priv、刷 TLB、改特权），必须考虑 `g_sys_state_flag`（`SYS_STATE_FLUSH_TCACHE` 等位）和 `rtl_priv_jr` 宏，否则 trace cache 会执行陈旧代码。
- **`CONFIG_SHARE=y`（difftest 模式）**：禁用 trace cache，逐指令 `fetch_decode` + 直接 dispatch，方便每条指令同步状态给外部 ref。

### 指令解码与实现的双层结构（RISC-V 64）

NEMU 用一套**自定义 DSL** 实现指令解码：

- `src/isa/riscv64/instr/decode.c` 是顶层 dispatch（`def_THelper(main)` 用 `def_INSTR_IDTAB("0000001 ????? ?...", R, rvm)` 模式匹配 opcode）。
- 各扩展子目录 `instr/{rvi,rvm,rva,rvc,rvd,rvf,rvb,rvk,rvv,priv}/` 各有 `decode.h` + `exec.h`：
  - `decode.h` 用 `def_THelper(name)` 进一步细分 funct3/funct7
  - `exec.h` 用 `def_EHelper(name)` 写 RTL（"register transfer language"，宏在 `local-include/rtl.h` 和 `include/rtl/*.h`）
- 所有指令名进 `src/isa/riscv64/include/isa-all-instr.h` 的 `INSTR_LIST` 宏，`MAP(INSTR_LIST, FILL_EXEC_TABLE)` 在 `cpu-exec.c` 展开成 `EXEC_ID_xxx → &&exec_xxx` 的跳转表。
- 加新指令：①在合适的 `instr/<ext>/decode.h` 里 `def_INSTR_TAB`；②`exec.h` 里 `def_EHelper`；③`isa-all-instr.h` 的对应 `f(name)` 宏列表里加名字。**忘了第三步会得到链接错而非编译错**。

### DASICS 扩展（本分叉重点）

代码以 `#ifdef CONFIG_RV_DASICS` 圈起，共 54 个 CSR + 2 条新指令，分布在：

- `src/isa/riscv64/local-include/csr.h:42-68` — DASICS_CSRS 宏（`dsmcfg`/`dumcfg`、`dsmbound0/1`、`dumbound0/1`、`dlcfg0`、`dlbound0..31`（16 组库边界对，每组 lo/hi 共 32 个）、`djcfg`、`djbound0lo..3hi`（4 组跳转边界对共 8 个）、`dmaincall`、`dretpc`、`dretpcfz`、`dfreason`）+ MPK_CSRS（`upkru`、`spkrs`、`spkctl`）
- `src/isa/riscv64/local-include/intr.h:44-61` — `EX_DUCF=24`、`EX_DSCF=25` 异常码；DASICS 与 MPK **共用** 24/25（不是 32-35），靠 `dfreason` 寄存器区分：`DFR_EF=1`/`DFR_LF=2`/`DFR_SF=3`/`DFR_JF=4` / `MFR_LF=5` / `MFR_SF=6`
- `src/isa/riscv64/system/priv.c:153-330` — `dasics_in_trusted_zone(pc)`、`dasics_ldst_helper`、`dasics_fetch_helper`、`dasics_check_trusted` 四个核心检查；CSR 访问控制（`csr_is_legal` 在 DASICS 启用时强制 PC ∈ trusted zone，否则直接 `panic`）
- `src/isa/riscv64/include/isa-all-instr.h:165-171,195,215` — `dasicscall_j`/`dasicscall_jr` 指令名注册（忘了加这里只链接错不编译错）
- `src/isa/riscv64/instr/decode.c:52-55` — opcode `00010` 在 funct3 = 000/001 时分到 DASICS call；第 88-95 行是 fetch_decode 中的 DASICS CFI hook
- `src/isa/riscv64/instr/rvi/control.h:45-72` — `dasicscall.j/jr` 的 EHelper（`rtl_set_dretpc` 设返回点 + jr 跳目标）
- `src/memory/vaddr.c:115-120,152-155` — Load/Store 路径中调用 `dasics_ldst_helper`；注意 `vaddr_ifetch` 传 `s=NULL` **不走** DASICS（取指检查全靠 `dasics_fetch_helper` 在 CFI 边界做）

修改 DASICS 行为时，**两侧（独立解释器 + ref 共享库）都要测**——`riscv64-xs-dasics_defconfig` 和 `riscv64-xs-dasics-ref_defconfig` 是一对，`riscv64-nutshell-dasics-ref_defconfig` 是 NutShell 平台变体。

#### DASICS 完整调研报告（必读）

`doc-nemu/dasics/` 下有完整的 DASICS 实现调研报告（10 篇 markdown，约 3000 行）。**遇到以下场景必须先读对应章节**，不要凭原始代码现猜：

| 场景 | 章节 | 路径 |
|------|------|------|
| 第一次接触 DASICS / 想了解保护域模型 | 总体架构 | `doc-nemu/dasics/01-overview.md` |
| 写/调 LibDASICS、需要查 CSR 编号、字段、写掩码 | CSR 寄存器 | `doc-nemu/dasics/02-csr-registers.md` |
| 改 `dasicscall.j/jr` 的 decode/exec、加新 DASICS 指令 | 指令扩展 | `doc-nemu/dasics/03-instructions.md` |
| 调访存/取指/跳转的边界检查、修 DASICS 异常误判 | 边界检查 | `doc-nemu/dasics/04-boundary-check.md` |
| 写 trap handler、需要分清 6 种 dfreason 含义、配 medeleg/sedeleg | 异常机制 | `doc-nemu/dasics/05-exception-mechanism.md` |
| 排查"复位后 DASICS 不生效"、跨域调用状态不对、嵌套调用问题 | 初始化与跨域 | `doc-nemu/dasics/06-init-and-trap.md` |
| 加 defconfig、改 difftest regcpy、配 CI、对接 XiangShan emu DUT | 配置与 difftest | `doc-nemu/dasics/07-config-and-difftest.md` |
| 想知道当前分支是否有 reg-protection、Scheme B 与 sreg gate 的区别 | reg-protection 分支 | `doc-nemu/dasics/08-reg-protection-branch.md` |
| 速查源文件位置、修改前的本地验证清单、术语表、FAQ、远程分支地图 | 附录 | `doc-nemu/dasics/09-appendix.md` |

报告入口与卡片速览：`doc-nemu/dasics/README.md`。

**报告快照时间**：2026-05-06，基于 commit `069c1a41`。如果代码后续有显著改动（特别是 reg-protection 主线集成），报告中"当前状态"类描述可能过时——结构性描述（CSR 编号、检查函数职责、defconfig 列表）的有效期更长。

**几个调研中确认的反直觉事实**（避免再踩坑）：
- 当前分支 `dasics-reg-protection` 与 `dasics-master` 同 commit，**没有任何寄存器保护代码**——reg-protection 工作分散在 tag `dasics-scheme-b-commit-1`（仅 1/5 完成）和远程分支 `origin/nemu-sreg-register-protection`，均未合入主线
- `dumcfg` 是 `dsmcfg` 的影子寄存器：写 `dumcfg` 实际改 `dsmcfg`（按 DUMCFG_MASK 限制 U 可写位），`reg.c` 的 dump 显示 dumcfg 时也读的是 dsmcfg 值
- `rtl_dasics_jcheck` RTL 宏**实现为空**，jal/jalr 路径上的钩子无运行时效果；所有跳转检查在 fetch 阶段统一做
- `vaddr_ifetch` 传 NULL，**不走** `dasics_ldst_helper`；DASICS 取指检查完全靠 `dasics_fetch_helper` 在前一条 CFI 触发点拦截
- 边界寄存器写入自动对齐 8 字节（`src & ~0x7`），写 `0x12345` 实际存 `0x12340`
- 复位后 `dsmcfg = 0`，`mcfg_uena=0` 视整个 U 模式为 trusted → DASICS **默认 no-op**，必须软件显式启用
- CI（`.github/workflows/ci.yml`）只触发 `master` 分支（不存在），且配置内**完全不覆盖** dasics defconfig；提交 DASICS 改动必须本地手动验三个 dasics defconfig

### 关键模块对应

| 目录 | 职责 |
|------|------|
| `src/monitor/` | 启动、参数解析、`sdb`（simple debugger）、watchpoint、镜像加载 |
| `src/checkpoint/` | SimPoint profiling、cpt 序列化（gz 压缩）、cpt 路径管理（C++）。`cpt_env.c` 是 boot/profile 状态机 |
| `src/cpu/difftest/` | difftest **DUT** 侧逻辑（dlopen ref、`difftest_step`、`difftest_skip_dut/ref`） |
| `src/isa/<isa>/difftest/` | difftest **ref/dut** 侧的 ISA 适配（`difftest_regcpy`、`difftest_memcpy`） |
| `src/engine/interpreter/` | RTL 宏在 host 上的实现（`c_op.h`、`fp.c`、softfloat 桥接） |
| `tools/qemu-dl-diff/` | 把 QEMU 包成 dlopen ref 的 patch + Makefile |
| `tools/qemu-socket-diff/`、`tools/kvm-diff/` | 另两种 ref 通信方式 |
| `tools/kconfig/`、`tools/fixdep/` | 从 Linux 内核拿过来的 Kconfig 工具链，build 时按需编 |
| `resource/gcpt_restore/` | checkpoint 恢复用的汇编 stub，烧到 0x80000000，bbl 烧到 0x800a0000 |

### 配置系统

`Kconfig` 是顶层入口，`source` 进 `src/isa/<isa>/Kconfig`、`src/memory/Kconfig`、`src/device/Kconfig`。`make <foo>_defconfig` 触发 `tools/kconfig` 处理 `configs/<foo>_defconfig`，生成 `.config` → `include/generated/autoconf.h` → 通过 `<common.h>` 暴露 `CONFIG_xxx` 宏。新加配置项要同时改 Kconfig 和（如有）defconfig。

## 文档 README 同步规则

修改以下相邻文档仓库时，必须检查对应仓库的 `README.md` 是否仍与内容、导航、文件名、术语和远程仓库名称一致：

- `doc-nemu`
- `../xiangshan-dasics/doc-xiangshan`

如果 README 已经过时，必须在同一次改动中同步更新，并验证 README 链接指向现有文件。

对 `doc-nemu`，重点检查 `dasics/` 和 `reg-protection/treg-zero/`。对 `doc-xiangshan`，重点检查 `treg-zero-design-log/`、`sreg-crypto-design-log/`、`paper-writing/` 和 `xiangshan/`。

## difftest 工作流（重点）

把 NEMU 当 ref 给 RTL/QEMU 用：

```bash
make riscv64-xs-ref_defconfig && make -j   # 出 -so
# 上层 RTL 仿真器（如 XiangShan emu）通过 --diff=<path-to>.so 加载
```

把 QEMU 当 ref 给 NEMU 用：

```bash
make menuconfig   # 勾 DIFFTEST + DIFFTEST_REF_QEMU_DL
make -j           # 顶层 Makefile 会自动 cd 到 tools/qemu-dl-diff 编 ref
make run IMG=... # 自动加 --diff=<DIFF_REF_SO>
```

NEMU 当 ref 给另一个 NEMU 用（自一致性测试）：`riscv64-dual-xs-ref_defconfig`，CI 会跑这一步。

## CI（`.github/workflows/ci.yml`）

每次 push/PR 到 `master` 时跑（注意此分叉默认分支是 `dasics-master`，CI 触发条件可能不匹配，提交前手动验：

1. `riscv64-xs_defconfig` → 编译 → 跑 `ready-to-run/linux.bin` 验启动
2. `riscv64-xs-novga_defconfig` → 编 gcpt_restore → `scripts/take.sh` → `scripts/restore.sh` 验 cpt
3. `riscv64-xs-ref_defconfig` → 编 .so 验 ref 形态
4. `riscv64-dual-xs-ref_defconfig` → dual-ref 验

提交涉及 ISA / 解码 / cpt / DASICS 时，**至少把这四种 defconfig 都本地编一遍**，CI 没覆盖到 dasics 配置。

## 实用提示

- 加日志：`Log()` / `Logtb()`（trace block 级）/ `Logti()`（trace instr 级，需 `CONFIG_DEBUG`）/ `Loge()`（end-of-loop 级）。`panic()` 直接挂掉。
- `MUXDEF(CONFIG_X, A, B)` / `IFDEF(CONFIG_X, ...)` / `IFNDEF` 是 `include/macro.h` 提供的预处理糖，用来代替到处写 `#ifdef`。
- 调试 trace cache 相关 bug 时先关 `CONFIG_PERF_OPT`（用 `*-debug-*` 配置）排除复杂控制流问题，再回来定位。
- 看汇编：`make gdb` 自动 `gdb --args` 启动；或加 `CONFIG_TRACE_INST_DASM`（要先 `CONFIG_DEBUG`）打全反汇编日志。
- `scripts/git.mk` 里的 `git_commit` 钩子是 NJU PA 教学环境留下的自动 commit，**默认通过 `ifdef __NOT_DEFINED` 分支跳过**，不会污染本地历史。
