# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

import sys
import shutil

from colorama import Fore, Style
from lib.core.data import options
from lib.core.decorators import locked
from lib.core.settings import IS_WINDOWS
from lib.view.colors import set_color, clean_color, disable_color

if IS_WINDOWS:
    from colorama.win32 import (
        FillConsoleOutputCharacter,
        GetConsoleScreenBufferInfo,
        STDOUT,
    )


class CLI:
    def __init__(self):
        self.last_in_line = False
        self.buffer = ""

        if not options["color"]:
            disable_color()

    @staticmethod
    def erase():
        if IS_WINDOWS:
            csbi = GetConsoleScreenBufferInfo()
            line = "\b" * int(csbi.dwCursorPosition.X)
            sys.stdout.write(line)
            width = csbi.dwCursorPosition.X
            csbi.dwCursorPosition.X = 0
            FillConsoleOutputCharacter(STDOUT, " ", width, csbi.dwCursorPosition)
            sys.stdout.write(line)
            sys.stdout.flush()

        else:
            sys.stdout.write("\033[1K")
            sys.stdout.write("\033[0G")

    @locked
    def in_line(self, string):
        self.erase()
        sys.stdout.write(string)
        sys.stdout.flush()
        self.last_in_line = True

    @locked
    def new_line(self, string="", do_save=True):
        if self.last_in_line:
            self.erase()

        if IS_WINDOWS:
            sys.stdout.write(string)
            sys.stdout.flush()
            sys.stdout.write("\n")
            sys.stdout.flush()

        else:
            sys.stdout.write(string + "\n")

        sys.stdout.flush()
        self.last_in_line = False
        sys.stdout.flush()

        if do_save:
            self.buffer += string
            self.buffer += "\n"

    def get_type_color(self, waf_result, status):
        source = waf_result.get("source", "Unknown")
        
        # Default
        code = "UNK"
        color = Fore.WHITE
        
        if 200 <= status < 300:
            code = "OK "
            color = Fore.GREEN + Style.BRIGHT
        elif 300 <= status < 400:
            code = "RED"
            color = Fore.YELLOW
        elif status >= 400:
            code = "ERR"
            color = Fore.RED
            
        # Override based on WAF/Server detection
        if "WAF" in source and "App Logic" not in source:
            code = "WAF"
            color = Fore.RED + Style.BRIGHT
        elif "App Logic" in source:
            code = "APP"
            color = Fore.CYAN + Style.BRIGHT
        elif any(x in source for x in ["Server", "Nginx", "Apache", "IIS", "Cloudflare", "AWS", "Infrastructure"]):
            code = "SYS"
            color = Fore.WHITE + Style.DIM
            
        return code, color

    def print_row(self, response, waf_result, full_url):
        time_str = response.datetime.split()[1]
        status_code = response.status
        size_str = response.size
        
        type_code, type_color = self.get_type_color(waf_result, status_code)
        
        source_str = waf_result.get("source", "")
        if source_str == "Unknown":
            source_str = ""
            
        url_str = response.url if full_url else "/" + response.full_path
        
        # Append redirect info if present with colored arrow
        if response.redirect:
            arrow = set_color("->", fore="yellow", style="bright")
            url_str += f" {arrow} {response.redirect}"
        
        # Pipe Color (Dark Grey / Bright Black)
        PIPE = Fore.BLACK + Style.BRIGHT + " | " + Style.RESET_ALL
        
        # Formatting (Fixed Widths)
        c_time = f"{time_str:<8}"
        c_code = f"{str(status_code):<4}"
        c_type = f"{type_code:<4}"
        c_size = f"{size_str:<8}"
        c_source = f"{source_str:<22}"
        c_url = f"{url_str}"
        
        # Apply Colors to Content
        if 200 <= status_code < 300:
            c_code = Fore.GREEN + c_code + Style.RESET_ALL
        elif 300 <= status_code < 400:
            c_code = Fore.YELLOW + c_code + Style.RESET_ALL
        elif status_code >= 400:
            c_code = Fore.RED + c_code + Style.RESET_ALL
            
        c_type = type_color + c_type + Style.RESET_ALL
        
        # Construct the Row
        row = f"{c_time}{PIPE}{c_code}{PIPE}{c_type}{PIPE}{c_size}{PIPE}{c_source}{PIPE}{c_url}"
        self.new_line(row)
        
        # Print history (redirect chain) on new lines if needed
        for redirect in response.history:
            arrow = set_color("-->", fore="yellow", style="bright")
            self.new_line(f"{arrow} {redirect}")

    def status_report(self, response, full_url, waf_result=None):
        if waf_result is None:
            waf_result = {"source": "Unknown", "waf_present": False}
        elif isinstance(waf_result, str):
             waf_result = {"source": waf_result, "waf_present": True}
             
        self.print_row(response, waf_result, full_url)

    def last_path(self, index, length, current_job, all_jobs, rate, errors):
        percentage = int(index / length * 100)
        task = set_color("#", fore="cyan", style="bright") * int(percentage / 5)
        task += " " * (20 - int(percentage / 5))
        progress = f"{index}/{length}"

        grean_job = set_color("job", fore="green", style="bright")
        jobs = f"{grean_job}:{current_job}/{all_jobs}"

        red_error = set_color("errors", fore="red", style="bright")
        errors = f"{red_error}:{errors}"

        progress_bar = f"[{task}] {str(percentage).rjust(2, chr(32))}% "
        progress_bar += f"{progress.rjust(12, chr(32))} "
        progress_bar += f"{str(rate).rjust(9, chr(32))}/s       "
        progress_bar += f"{jobs.ljust(21, chr(32))} {errors}"

        if len(clean_color(progress_bar)) >= shutil.get_terminal_size()[0]:
            return

        self.in_line(progress_bar)

    def new_directories(self, directories):
        message = set_color(
            f"Added to the queue: {', '.join(directories)}", fore="yellow", style="dim"
        )
        self.new_line(message)

    def error(self, reason):
        message = set_color(reason, fore="white", back="red", style="bright")
        self.new_line("\n" + message)

    def warning(self, message, do_save=True):
        message = set_color(message, fore="yellow", style="bright")
        self.new_line(message, do_save=do_save)

    def header(self, message):
        message = set_color(message, fore="blue", style="bright")
        self.new_line(message)

    def print_header(self, headers):
        for key, value in headers.items():
            prefix = set_color("[+]", fore="green", style="bright")
            key_str = set_color(f"{key.upper():<12}", fore="white", style="bright")
            sep = set_color(":", fore="white", style="dim")
            val_str = set_color(str(value), fore="cyan", style="bright")
            
            self.new_line(f"{prefix} {key_str} {sep} {val_str}")

    def config(self, wordlist_size):
        config = {}
        
        # We rely on self.target() being called separately or we can add it here if available
        # But usually target is printed by self.target()
        
        config["Method"] = options["http_method"]
        config["Threads"] = str(options["thread_count"])
        config["Wordlist"] = f"{wordlist_size} items"
        
        if options["extensions"]:
            config["Extensions"] = ", ".join(options["extensions"])
            
        if options["prefixes"]:
            config["Prefixes"] = ", ".join(options["prefixes"])
            
        if options["suffixes"]:
            config["Suffixes"] = ", ".join(options["suffixes"])

        self.print_header(config)

    def target(self, target):
        self.new_line()
        self.print_header({"Target": target})

    def log_file(self, file):
        self.new_line(f"\nLog File: {file}")


class QuietCLI(CLI):
    def status_report(self, response, full_url):
        super().status_report(response, True)

    def last_path(*args):
        pass

    def new_directories(*args):
        pass

    def warning(*args, **kwargs):
        pass

    def header(*args):
        pass

    def config(*args):
        pass

    def target(*args):
        pass

    def log_file(*args):
        pass


class EmptyCLI(QuietCLI):
    def status_report(*args):
        pass

    def error(*args):
        pass


interface = EmptyCLI() if options["disable_cli"] else QuietCLI() if options["quiet"] else CLI()
