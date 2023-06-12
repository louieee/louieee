from itertools import chain

from decouple import config
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property


# Create your models here.

class LanguageLevel(models.TextChoices):
	CONVERSATIONAL = ("Conversational", "Conversational")


class Job(models.Model):
	name = models.CharField(max_length=255)
	foreign = models.BooleanField(default=False)
	country = models.CharField(max_length=200)
	resumes = models.ManyToManyField("Resumee")

	def __str__(self):
		return self.name


class Template(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return self.name


def calculate_month(days=0):
	if days // 28 == 0:
		return ""
	return f"{days // 28} month{'s' if days > 56 else ''}"


def duration(start_date, end_date):
	end_date = end_date if end_date else timezone.now().date()
	d = end_date - start_date
	if d.days < 28:
		return "Less than a month"
	elif 28 <= d.days < 365:
		return calculate_month(d.days)
	else:
		years = d.days // 365
		days = d.days % 365
		return f"{years} year{'s' if years > 1 else ''} {calculate_month(days)}"


class Resumee(models.Model):
	title = models.CharField(max_length=200, default=None, null=True)
	first_name = models.CharField(max_length=255)
	middle_name = models.CharField(max_length=255, blank=True)
	surname = models.CharField(max_length=255)
	contact = models.CharField(max_length=20, blank=True, default="")
	roles = models.CharField(max_length=255, blank=True, default="")
	email = models.EmailField(max_length=255)
	website = models.URLField(max_length=255, blank=True)
	state = models.CharField(max_length=200, blank=True)
	country = models.CharField(max_length=200, blank=True)
	github_link = models.URLField(max_length=255)
	linkedin_link = models.URLField(max_length=255)
	profile_pic = models.ImageField(upload_to="resumee", null=True, blank=True)
	objective = models.TextField()
	work_history = models.ManyToManyField("WorkExperience")
	education_history = models.ManyToManyField("Education")
	template = models.ForeignKey("Template", on_delete=models.SET_NULL, null=True, blank=True)
	active = models.BooleanField(default=False)
	portfolios = models.ManyToManyField("Portfolio", blank=True)
	languages = models.ManyToManyField("Language", blank=True)

	def __str__(self):
		return f"{self.first_name} {self.surname} V{self.id}"

	@cached_property
	def referees(self):
		return Referee.objects.filter(Q(work_experience_id__in=self.work_history.values_list("id", flat=True)) |
		                              Q(education_id__in=self.education_history.values_list("id", flat=True))). \
			order_by("name")

	@cached_property
	def skills(self):
		skill_ids = list(set(chain(*[x.skills for x in self.work_history.all()])))
		return Skill.objects.filter(id__in=skill_ids).order_by("-degree")

	def duplicate(self):
		resumee = Resumee()
		resumee.first_name = self.first_name
		resumee.middle_name = self.middle_name
		resumee.surname = self.surname
		resumee.email = self.email
		resumee.website = self.website
		resumee.github_link = self.github_link
		resumee.linkedin_link = self.linkedin_link
		resumee.objective = self.objective
		resumee.template = self.template
		resumee.save()
		resumee.work_history.add(*self.work_history.all())
		resumee.education_history.add(*self.education_history.all())
		resumee.save()

	def activate(self):
		Resumee.objects.filter(~Q(id=self.id)).update(active=False)
		self.active = True
		self.save()
		return

	@cached_property
	def years_of_experience(self):
		we = WorkExperience.objects.filter(resumee=self).order_by("start_date").first()
		if we:
			return (timezone.now().date() - we.start_date).days / 365
		return 0

	@cached_property
	def number_of_clients(self):
		return self.portfolios.values_list("client").distinct().count()

	@cached_property
	def profile_url(self):
		if self.profile_pic:
			return f"{config('BASE_URL')}{self.profile_pic.url}"
		return None


class Skill(models.Model):
	name = models.CharField(max_length=255)
	degree = models.PositiveSmallIntegerField(default=100)
	order = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return self.name


class Language(models.Model):
	name = models.CharField(max_length=100)
	level = models.CharField(choices=LanguageLevel.choices, default=LanguageLevel.CONVERSATIONAL, max_length=100)


class Portfolio(models.Model):
	name = models.CharField(max_length=200)
	company = models.CharField(max_length=200)
	client = models.CharField(max_length=200)
	category = models.CharField(max_length=200, default="", blank=True)
	date_started = models.DateField()
	date_ended = models.DateField()
	description = models.TextField()
	link = models.URLField()

	def __str__(self):
		return self.name

	@cached_property
	def duration(self):
		return duration(self.date_started, self.date_ended)

	@cached_property
	def images(self):
		return [x.get_url() for x in PortfolioImage.objects.filter(portfolio=self)]


class PortfolioImage(models.Model):
	portfolio = models.ForeignKey("Portfolio", on_delete=models.CASCADE)
	image = models.ImageField(upload_to="portfolio")

	def __str__(self):
		return f"{self.portfolio.name}||{self.image.name}"

	def get_url(self):
		if self.image:
			return f'{config("BASE_URL")}{self.image.url}'
		return None


class WorkExperienceDescription(models.Model):
	work_experience = models.ForeignKey('WorkExperience', on_delete=models.CASCADE)
	description = models.TextField()
	skills = models.ManyToManyField("Skill", blank=True)
	order = models.PositiveSmallIntegerField(default=0)

	def __str__(self):
		return f"WE{self.work_experience.id}=> {self.description}"


class WorkType(models.TextChoices):
	FULL_TIME = ("Full Time", "Full Time")
	PART_TIME = ("Part Time", "Part Time")
	CONTRACT = ("Contract", "Contract")


class WorkExperience(models.Model):
	role = models.CharField(max_length=255)
	company = models.CharField(max_length=255)
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)
	company_location = models.CharField(max_length=255)
	work_type = models.CharField(choices=WorkType.choices, default=WorkType.FULL_TIME, max_length=30)

	def __str__(self):
		return f"{self.role} at {self.company} in {self.start_date.year}"

	@cached_property
	def skills(self):
		v = filter(lambda x: x is not None,
		           WorkExperienceDescription.objects.filter(work_experience=self).values_list("skills__id", flat=True). \
		           distinct())
		return list(set(chain(v)))

	@cached_property
	def descriptions(self):
		return WorkExperienceDescription.objects.filter(work_experience=self).order_by("order") \
			.values_list("description", flat=True)

	@cached_property
	def duration(self):
		return duration(self.start_date, self.end_date)


class Education(models.Model):
	field_of_study = models.CharField(max_length=255)
	degree = models.CharField(max_length=255)
	grade = models.CharField(max_length=255)
	institution = models.CharField(max_length=255)
	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"{self.field_of_study} in {self.institution} at {self.start_date.year}"

	def duration(self):
		return duration(self.start_date, self.end_date)


class Referee(models.Model):
	name = models.CharField(max_length=255)
	role = models.CharField(max_length=255)
	email = models.EmailField()
	contact = models.CharField(max_length=30)
	work_experience = models.ForeignKey("WorkExperience", on_delete=models.SET_NULL, null=True)
	education = models.ForeignKey("Education", on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return f"{self.role} at {self.work_experience.company if self.work_experience else self.education.institution}"
