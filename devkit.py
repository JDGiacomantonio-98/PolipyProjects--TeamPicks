def set_env(selKey):
	from os import path, getenv
	from dotenv import load_dotenv

	envs = {
		'd': 'development',
		't': 'testing',
		'p': 'production',
	}

	basedir = path.abspath(path.dirname(__file__))
	load_dotenv(path.join(basedir, '.env'))
	e = getenv('FLASK_ENV')
	if e is None:
		with open(path.join(basedir, '.env'), 'a') as f:
			f.write(f'\nFLASK_ENV={envs[selKey]}')
			return envs[selKey]
	elif e != envs[selKey]:
		with open(path.join(basedir, '.env'), 'r') as f:
			lines = f.readlines()
		with open(path.join(basedir, '.env'), 'w') as f:
			for line in lines:
				if 'FLASK_ENV=' in line:
					f.write(f'FLASK_ENV={envs[selKey]}')
				else:
					f.write(line)
	return envs[selKey]


def create_userbase(items=None, test_db=False):
	from math import floor
	from random import randint

	from faker import Faker

	from app.dbModels import dummy, Owner

	userbase = {
		'owner': 'o',
		'user': 'u'
	}

	set_roles()
	if not test_db:
		if items is None:
			items = (input('Please select how many object will the userbase be composed of :\t'))
			while not items.isnumeric():
				print('Input error: only a numeric value can be submitted. Try again.')
				items = (input('Please select how many object will the userbase be composed of :\t'))
		elif type(items) != int:
			while not items.isnumeric():
				print('Input error: only a numeric value can be submitted. Try again.')
				items = (input('Please select how many object will the userbase be composed of :\t'))
		items = int(items)
		cities = []
		faker = Faker(['en_US', 'en_GB', 'zh_CN', 'fr_FR', 'es_ES', 'it_IT'])
		K_CITY = 0.8 # a-priori known value of the population propensity to live where also others live (network externalities effect)
		for _ in range(randint(1, ((items + 1) - floor(K_CITY*items)))):
			cities.append(faker.city().lower())
		for k in userbase:
			if k == 'user':
				dummy(return_obj=False, model=userbase[k], items=items, o_mass=Owner.query.count(), cities=cities)
			else:
				dummy(return_obj=False, model=userbase[k], items=items, cities=cities)
	else:
		for k in userbase:
			try:
				if k == 'user':
					dummy(return_obj=False, model=userbase[k], o_mass=Owner.query.count(), db_w_test=test_db)
				else:
					dummy(return_obj=False, model=userbase[k], db_w_test=test_db)
			except RuntimeError:
				return None


def set_roles():
	from app import db
	from app.dbModels import G_PERMISSIONS, G_Role

	perm = G_PERMISSIONS()
	roles = {
		'admin': perm.admin(),
		'manager': perm.manager(),
		'moderator': perm.moderator(),
		'member': perm.member()
	}
	default = 'member'
	for r in roles:
		itm = G_Role.query.filter_by(role=r).first()
		if itm is None:
			itm = G_Role(role=r)
		itm.add_permission(roles[r])
		itm.is_default = (itm.role == default)
		db.session.add(itm)
	db.session.commit()


def config_menu():
	# print a menu to create different instances of app working with different Configs profiles
	choices = ['', 'd', 't', 'p', 'q']
	print('==================')
	k = str(input('SELECT APP ENV (on this machine)\n'
				  '==================\n'
				  '[D]evelopment\n'
				  '[T]esting\n'
				  '[P]roduction\n\n'
				  '[Q]uit process\n'
				  'press < Enter > to run Defaults :\t'
				  )
			).lower()
	while k.isnumeric() or (k not in choices):
		print('Invalid input : please choose from menu options.')
		k = str(input('SELECT APP ENV (on this machine)\n'
					  '==================\n'
					  '[D]evelopment\n'
					  '[T]esting\n'
					  '[P]roduction\n\n'
					  '[Q]uit process\n'
					  'press < Enter > to run Defaults :\t'
					  )
				).lower()
	if k == 'q':
		quit()
	if k == '':
		k = 'd'
	return k
