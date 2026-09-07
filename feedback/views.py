import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from accounts.permissions import api_login_required
from feedback.models import FeedbackCard
from retros.models import Retro

def _card(card, user):
    return {"id": card.pk, "category": card.category, "text": card.text, "anonymous": card.anonymous, "author": None if card.anonymous and card.author_id != user.pk else {"id": card.author_id, "username": card.author.username}}

@require_http_methods(["GET", "POST"])
@api_login_required
def collection(request, retro_id):
    retro = get_object_or_404(Retro, pk=retro_id, team__memberships__user=request.user)
    if request.method == "GET":
        cards = retro.feedback_cards.all() if retro.stage != Retro.Stage.COLLECTING else retro.feedback_cards.filter(author=request.user)
        return JsonResponse({"cards": [_card(card, request.user) for card in cards]})
    if retro.stage != Retro.Stage.COLLECTING: return JsonResponse({"detail": "Feedback collection is closed."}, status=400)
    try: data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError): return JsonResponse({"detail": "Invalid JSON."}, status=400)
    if data.get("category") not in FeedbackCard.Category.values or not isinstance(data.get("text"), str) or not data["text"].strip() or not isinstance(data.get("anonymous", False), bool): return JsonResponse({"detail": "Invalid feedback fields."}, status=400)
    card = FeedbackCard.objects.create(retro=retro, author=request.user, category=data["category"], text=data["text"].strip(), anonymous=data.get("anonymous", False))
    return JsonResponse({"card": _card(card, request.user)}, status=201)

@require_http_methods(["PATCH", "DELETE"])
@api_login_required
def detail(request, retro_id, card_id):
    retro = get_object_or_404(Retro, pk=retro_id, team__memberships__user=request.user)
    card = get_object_or_404(FeedbackCard, pk=card_id, retro=retro, author=request.user)
    if retro.stage != Retro.Stage.COLLECTING:
        return JsonResponse({"detail": "Feedback can only be changed while collecting."}, status=400)
    if request.method == "DELETE":
        card.delete()
        return JsonResponse({}, status=204)
    try: data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError): return JsonResponse({"detail": "Invalid JSON."}, status=400)
    for field in ("category", "text", "anonymous"):
        if field in data: setattr(card, field, data[field])
    if card.category not in FeedbackCard.Category.values or not isinstance(card.text, str) or not card.text.strip() or not isinstance(card.anonymous, bool):
        return JsonResponse({"detail": "Invalid feedback fields."}, status=400)
    card.text = card.text.strip()
    card.save()
    return JsonResponse({"card": _card(card, request.user)})
