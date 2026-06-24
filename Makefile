NAME = skyscraper_solver

CC = gcc
CFLAGS = -Wall -Wextra -Werror -O2

SRC_DIR = src
OBJ_DIR = obj

SRCS = $(wildcard $(SRC_DIR)/*.c)

OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

ifeq ($(OS),Windows_NT)
	BINARY = $(NAME).exe
	CLEAN_CMD = if exist $(OBJ_DIR) rmdir /S /Q $(OBJ_DIR)
	FCLEAN_CMD = if exist $(BINARY) del /Q /F $(BINARY)
	MKDIR_CMD = if not exist $(OBJ_DIR) mkdir $(OBJ_DIR)
else
	BINARY = $(NAME)
	CLEAN_CMD = rm -rf $(OBJ_DIR)
	FCLEAN_CMD = rm -f $(BINARY)
	MKDIR_CMD = mkdir -p $(OBJ_DIR)
endif

all: $(BINARY)

$(BINARY): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(BINARY)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c | $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR):
	$(MKDIR_CMD)

clean:
	$(CLEAN_CMD)

fclean: clean
	$(FCLEAN_CMD)

re: fclean all

test: $(BINARY)
	python3 python_scripts/verify_consistency.py -r $(BINARY)

.PHONY: all clean fclean re test
