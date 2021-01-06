/*
 * main.cpp
 * 
 * Copyright (C) 2021, Universidade Federal de Santa Catarina.
 * 
 * This file is part of SpaceLab-Decoder.
 * 
 * SpaceLab-Decoder is free software: you can redistribute it
 * and/or modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 * 
 * SpaceLab-Decoder is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with SpaceLab-Decoder. If not, see <http://www.gnu.org/licenses/>.
 * 
 */

/**
 * \brief Main file.
 * 
 * \author Gabriel Mariano Marcelino <gabriel.mm8@gmail.com>
 * 
 * \version 0.2.13
 * 
 * \date 2021/01/06
 * 
 * \note Reference: https://docs.python.org/3/extending/embedding.html
 *
 * \defgroup spacelab-decoder SpaceLab Decoder
 * \{
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <unistd.h>

#define PYTHON_MAIN_FILE_PATH           "/usr/share/spacelab-decoder/main.py"
#define PYTHON_MAIN_FILE_LOCAL_PATH     "spacelab-decoder/main.py"

int main(int argc, char *argv[])
{
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);

    if (program == NULL)
    {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n\r");
        exit(1);
    }

    Py_SetProgramName(program); /* optional but recommended */
    Py_Initialize();

    FILE *fd = NULL;

    /* Verifies if a local Python script exists */
    if (access(PYTHON_MAIN_FILE_LOCAL_PATH, F_OK) != -1)
    {
        fd = fopen(PYTHON_MAIN_FILE_LOCAL_PATH, "r");

        if (fd)
        {
            PyRun_SimpleFile(fd, PYTHON_MAIN_FILE_LOCAL_PATH);

            fclose(fd);
        }
    }
    else
    {
        fd = fopen(PYTHON_MAIN_FILE_PATH, "r");

        if (fd)
        {
            PyRun_SimpleFile(fd, PYTHON_MAIN_FILE_PATH);

            fclose(fd);
        }
    }

    if (Py_FinalizeEx() < 0)
    {
        exit(120);
    }

    PyMem_RawFree(program);

    return 0;
}

/**< \} End of spacelab-decoder group */
