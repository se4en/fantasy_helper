from aiogram.utils.callback_data import CallbackData

menu_callback = CallbackData("menu", "choice_name")

coeffs_callback = CallbackData("coeffs", "league_name", "round")

players_callback = CallbackData("players", "league_name")

stats_callback = CallbackData("stats", "league_name", "type", "last_5")

sources_callback = CallbackData("sources", "league_name", "action")

admin_callback = CallbackData("admin", "tool_name", "league_name")
