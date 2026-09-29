RESOURCE_PATH := $(NEMU_HOME)/resource

include $(NEMU_HOME)/scripts/softfloat.mk

# Shared references do not compile checkpoint code or consume its dependencies.
# An unconfigured tree must also remain free of parse-time dependency fetches.
clean-repos: clean-softfloat
ifneq ($(CONFIG_SHARE),y)
ifeq ($(CONFIG_LIBCHECKPOINT_RESTORER),y)
include $(NEMU_HOME)/scripts/nanopb.mk
include $(NEMU_HOME)/scripts/Libcheckpoint.mk
clean-repos: clean-libcheckpoint
endif
ifeq ($(CONFIG_LIBCHECKPOINT_ALPHA_RESTORER),y)
include $(NEMU_HOME)/scripts/LibcheckpointAlpha.mk
clean-repos: clean-libcheckpointalpha
endif
endif
