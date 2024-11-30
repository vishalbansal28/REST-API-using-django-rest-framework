import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Show, Role, Quote

def add_sample_data():
    """Add movie quotes with explicit language for adult content testing"""
    shows_data = [
        {
            'name': 'Pulp Fiction',
            'slug': 'pulp-fiction',
            'roles': [
                {
                    'name': 'Jules Winnfield',
                    'quotes': [
                        ("What the f%ck did you just say?", True),
                        ("English motherf%cker, do you speak it?", True),
                        ("This is some serious sh%t!", True),
                        ("I'm tired of this motherf%cking sh%t!", True)
                    ]
                },
                {
                    'name': 'Vincent Vega',
                    'quotes': [
                        ("This is some f%cked up repugnant sh%t.", True),
                        ("I'm about to get f%cking medieval on you.", True),
                        ("Aw man, I shot Marvin in the f%cking face!", True),
                        ("That's some cold-blooded sh%t!", True)
                    ]
                }
            ]
        },
        {
            'name': 'The Big Lebowski',
            'slug': 'the-big-lebowski',
            'roles': [
                {
                    'name': 'Walter Sobchak',
                    'quotes': [
                        ("This is what happens when you f%ck a stranger!", True),
                        ("Shut the f%ck up, Donny!", True),
                        ("You see what happens? This is what happens when you f%ck with us!", True),
                        ("You're entering a world of f%cking pain!", True)
                    ]
                },
                {
                    'name': 'The Dude',
                    'quotes': [
                        ("This is what happens when you f%ck with the Jesus!", True),
                        ("F%ck it dude, let's go bowling.", True),
                        ("This is a f%cking show dog.", True),
                        ("That f%cking b%tch!", True)
                    ]
                }
            ]
        },
        {
            'name': 'Scarface',
            'slug': 'scarface',
            'roles': [
                {
                    'name': 'Tony Montana',
                    'quotes': [
                        ("You f%cking with the wrong guy!", True),
                        ("You f%cking cockroach!", True),
                        ("You f%cking piece of sh%t!", True),
                        ("Look at you now, you f%cking worm!", True)
                    ]
                }
            ]
        }
    ]

    # Add shows, roles, and quotes
    for show_data in shows_data:
        show, created = Show.objects.get_or_create(
            name=show_data['name'],
            defaults={'slug': show_data['slug']}
        )
        if created:
            print(f"Created new show: {show.name}")
        else:
            print(f"Show already exists: {show.name}")

        for role_data in show_data['roles']:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                show=show
            )
            if created:
                print(f"Created new role: {role.name}")
            else:
                print(f"Role already exists: {role.name}")

            for quote_text, is_adult in role_data['quotes']:
                quote, created = Quote.objects.get_or_create(
                    quote=quote_text,
                    defaults={
                        'show': show,
                        'role': role,
                        'contain_adult_lang': is_adult
                    }
                )
                if created:
                    print(f"Created new quote: {quote_text[:50]}... [Adult: {'Yes' if is_adult else 'No'}]")
                else:
                    print(f"Quote already exists: {quote_text[:50]}...")

    print("\nSample data has been added successfully!")

if __name__ == '__main__':
    add_sample_data()
