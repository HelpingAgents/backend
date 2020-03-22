import random

from django.utils.deprecation import MiddlewareMixin


corona_facts = [
    "Das Coronavirus kann durch Händeschütteln, gefolgt von einer Berührung des Gesichts, übertragen werden. Stattdessen kann man andere durch Winken, Nicken oder Verbeugen begrüßen.",
    "Selbst mit Handschuhen kann man sich infizieren, wenn man eine kontaminierte Oberfläche berührt und anschließend das Gesicht berührt. Achten Sie stattdessen darauf, Ihre Hände zu waschen!",
    "Wenn Sie Kurzatmigkeit (shortness of breath) entwickeln, rufen Sie sofort Ihren Arzt an!",
    "Waschen Sie Ihre Hände nach dem Husten oder Niesen.",
    "Vergessen Sie nicht, sich vor, während und nach der Zubereitung von Speisen die Hände zu waschen.",
    "Fühlen Sie sich allein? Rufen Sie die Support Line unter XXX an.",
    "Auch wenn es schwierig ist, tun Sie Ihr Bestes, um einen gesunden Lebensstil zu erhalten. Achten Sie auf einen angemessenen Schlafzyklus, Ernährung, Bewegung und soziale Kontakte.",
    "Social Distancing? Was bedeutet das? Wenn jemand hustet oder niest, versprüht er kleine Flüssigkeitstropfen aus der Nase oder dem Mund, die Viren enthalten können. Wenn man zu nahe dran ist, kann man die Tröpfchen einatmen und erkranken.",
]


class DisableCSRF(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)


def get_random_corona_fact():
    return random.choice(corona_facts)


def say(resp, text):
    resp.say(text, language="de-DE")
