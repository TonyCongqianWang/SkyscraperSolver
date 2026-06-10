NAME = skyscraper_solver

CC = gcc
CFLAGS = -Wall -Wextra -Werror -O2

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
       $(SRC_DIR)/node_pruning.c \
       $(SRC_DIR)/node_selection.c \
       $(SRC_DIR)/print_grid.c \
       $(SRC_DIR)/print_utlilty.c \
       $(SRC_DIR)/puzzle_init.c \
       $(SRC_DIR)/puzzle_solver.c \
       $(SRC_DIR)/rule_checking.c \
       $(SRC_DIR)/solution_info.c \
       $(SRC_DIR)/solution_storage.c \
       $(SRC_DIR)/string_interface.c \
       $(SRC_DIR)/transition_scoring.c \
       $(SRC_DIR)/tree_search.c \
       $(SRC_DIR)/strategy_routing.c \
       $(SRC_DIR)/prune_lookahead.c \
       $(SRC_DIR)/prune_gac.c \
       $(SRC_DIR)/prune_gac_domain.c \
       $(SRC_DIR)/prune_gac_naked.c \
       $(SRC_DIR)/prune_gac_hidden.c \
       $(SRC_DIR)/node_selection_score.c \
       $(SRC_DIR)/node_selection_cache.c \
       $(SRC_DIR)/node_selection_eval.c \
       $(SRC_DIR)/node_selection_utils.c \
       $(SRC_DIR)/node_selection_cache_helper.c

OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(NAME)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

clean:
	rm -rf $(OBJ_DIR)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
