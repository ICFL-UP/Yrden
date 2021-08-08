from django.utils import timezone


def run_plugin_modules_5_job():
    print('running job ' + timezone.now().strftime('%Y-%m-%d %H:%M:%S'))

# This should be moved out (only using this for testing until the crontabs are set up fully)
# =============================================

# def walk_plugins(plugin: Plugin):
#     import os
#     import subprocess

#     dir = 'core/plugin'
#     for fname in os.listdir(dir):
#         main = dir + os.sep + fname + os.sep + 'main.py'
#         if fname.lower() == str(plugin.name).lower() and os.path.isfile(main):
#             process = subprocess.run(['python', main], check=True, stdout=subprocess.PIPE)
#             output = process.stdout


# qs = Plugin.objects.all()
# for plugin in qs:
#     walk_plugins(plugin)

# =============================================
