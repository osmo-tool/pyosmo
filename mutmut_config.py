def pre_mutation(context):
    if context.filename == 'setup.py':
        context.skip = True
    line = context.current_source_line.strip()
    if line.startswith('log'):
        context.skip = True
