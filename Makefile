NAME = skyscraper_solver

CC = gcc
CFLAGS = -Wall -Wextra -Werror -O2

ifeq ($(OS),Windows_NT)
	LDFLAGS = -Wl,--stack,8388608
	BINARY = $(NAME).exe
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		LDFLAGS = -Wl,-z,stack-size=8388608
	endif
	ifeq ($(UNAME_S),Darwin)
		LDFLAGS = -Wl,-stack_size,0x800000
	endif
	BINARY = ./$(NAME)
endif

SRC_DIR = src
OBJ_DIR = obj

SRCS = $(SRC_DIR)/main.c \
	$(SRC_DIR)/argument_parsing.c \
	$(SRC_DIR)/cell_bounds.c \
	$(SRC_DIR)/constraint_checking.c \
	$(SRC_DIR)/constraint_selection.c \
	$(SRC_DIR)/constraint_update.c \
	$(SRC_DIR)/grid_availability.c \
	$(SRC_DIR)/grid_manipulation.c \
	$(SRC_DIR)/grid_update.c \
	$(SRC_DIR)/lookahead_dive.c \
	$(SRC_DIR)/node_selection.c \
	$(SRC_DIR)/node_selection_cache.c \
	$(SRC_DIR)/node_selection_cache_api.c \
	$(SRC_DIR)/node_selection_cache_helper.c \
	$(SRC_DIR)/node_selection_cache_api_next.c \
	$(SRC_DIR)/node_selection_eval.c \
	$(SRC_DIR)/node_selection_score.c \
	$(SRC_DIR)/node_selection_utils.c \
	$(SRC_DIR)/print_grid.c \
	$(SRC_DIR)/print_utlilty.c \
	$(SRC_DIR)/pruning_routines.c \
	$(SRC_DIR)/prune_check_constr.c \
	$(SRC_DIR)/prune_check_constr_dp.c \
	$(SRC_DIR)/prune_check_constr_utils.c \
	$(SRC_DIR)/prune_initial.c \
	$(SRC_DIR)/prune_root.c \
	$(SRC_DIR)/prune_shallow.c \
	$(SRC_DIR)/prune_medium.c \
	$(SRC_DIR)/prune_deep.c \
	$(SRC_DIR)/prune_gac.c \
	$(SRC_DIR)/prune_gac_domain.c \
	$(SRC_DIR)/prune_gac_hidden.c \
	$(SRC_DIR)/prune_gac_naked.c \
	$(SRC_DIR)/prune_lookahead.c \
	$(SRC_DIR)/prune_strat_routing.c \
	$(SRC_DIR)/puzzle_init.c \
	$(SRC_DIR)/puzzle_solver.c \
	$(SRC_DIR)/rule_checking.c \
	$(SRC_DIR)/sel_strat_routing.c \
	$(SRC_DIR)/solution_info.c \
	$(SRC_DIR)/solution_storage.c \
	$(SRC_DIR)/string_interface.c \
	$(SRC_DIR)/transition_scoring.c \
	$(SRC_DIR)/tree_search.c \
	$(SRC_DIR)/tree_search_step.c

OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) $(OBJS) -o $(NAME)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR):
ifeq ($(OS),Windows_NT)
	@if not exist $(OBJ_DIR) mkdir $(OBJ_DIR)
else
	mkdir -p $(OBJ_DIR)
endif

clean:
ifeq ($(OS),Windows_NT)
	@if exist $(OBJ_DIR) rmdir /S /Q $(OBJ_DIR)
else
	rm -rf $(OBJ_DIR)
endif

fclean: clean
ifeq ($(OS),Windows_NT)
	@if exist $(NAME).exe del /Q /F $(NAME).exe
	@if exist $(NAME) del /Q /F $(NAME)
else
	rm -f $(NAME)
endif

re: fclean all

test: $(NAME)
	python3 python_scripts/verify_consistency.py -r $(BINARY)

.PHONY: all clean fclean re test
