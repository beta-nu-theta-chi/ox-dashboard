def cleaned_brother_data(line):
    stripped_data = [data.strip() for data in line.strip().split(",")]

    for i in range(len(stripped_data), 3):
        stripped_data.append("")

    return stripped_data[0:3]


def can_brother_be_added(first_name, last_name, caseid):
    data = [first_name, last_name, caseid]

    return all(value != "" for value in data) and not Brother.objects.filter(case_ID=caseid).exists()


def create_brother_if_possible(semester, brother_status, first_name, last_name, caseid):
    if User.objects.filter(username=caseid).exists():
        user = User.objects.get(username=caseid)
    elif caseid != "":
        user = User()
        user.username = caseid
        user.save()
    else:
        pass  # nothing to do here since the if below will return false
                # ie `user` is never accessed

    # if able to add, create the brother with the given data
    if can_brother_be_added(first_name, last_name, caseid):
        new_brother = Brother()
        new_brother.user = user
        new_brother.first_name = first_name
        new_brother.last_name = last_name
        new_brother.case_ID = user.username
        new_brother.birthday = datetime.date.today()
        new_brother.semester = semester
        new_brother.brother_status = brother_status
        new_brother.save()


def create_mass_entry_brothers(request, mass_entry_form):
    if mass_entry_form.is_valid():
        data = mass_entry_form.cleaned_data
        brother_data = data["brothers"].split("\n")
        semester = data["semester"]
        brother_status = data["brother_status"]

        for brother in brother_data:
            create_brother_if_possible(semester, brother_status, *cleaned_brother_data(brother))

    else:
        messages.error(request, "Mass entry form invalid")


def staged_mass_entry_brothers(mass_entry_form):
    brothers = []
    mass_entry_form.fields['brothers'].widget.attrs['readonly'] = True
    if mass_entry_form.is_valid():
        data = mass_entry_form.cleaned_data
        brother_data = data["brothers"].split("\n")

        for brother in brother_data:

            first, last, caseid = cleaned_brother_data(brother)

            brothers.append({
                'first_name': first,
                'last_name': last,
                'caseid': caseid,
                'will_be_added': can_brother_be_added(first, last, caseid)
            })

    return brothers


def brother_mass_entry_form(request):
    brothers = []

    if request.method == 'POST':
        mass_entry_form = BrotherMassEntryForm(request.POST)
        mass_entry_form.fields['brothers'].widget.attrs['readonly'] = False
        is_entry = False

        if "confirmation" in request.POST:
            create_mass_entry_brothers(request, mass_entry_form)
            return HttpResponseRedirect(reverse('dashboard:home'))

        elif "goback" in request.POST:
            is_entry = True  # just want to go back to adding/editting data

        # however else we got here, we need to show the staged data
        else:
            brothers = staged_mass_entry_brothers(mass_entry_form)
    else:
        mass_entry_form = BrotherMassEntryForm()
        is_entry = True

    return mass_entry_form, is_entry, brothers
