def pre_mutation(context):
    if context.filename == 'setup.py':
        context.skip = True