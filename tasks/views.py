import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .scoring import calculate_scores


@csrf_exempt
def analyze_tasks(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        if isinstance(data, dict):
            tasks = data.get("tasks", [])
            weights = data.get("weights")
        elif isinstance(data, list):
            tasks = data
            weights = None
        else:
            return HttpResponseBadRequest("Invalid JSON format")

        scored = calculate_scores(tasks, weights)
        return JsonResponse(scored, safe=False)

    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def suggest_tasks(request):
    tasks_json = request.GET.get("tasks")

    if not tasks_json:
        return JsonResponse({"error": "Use ?tasks=<json array>"}, status=400)

    try:
        tasks = json.loads(tasks_json)
        scored = calculate_scores(tasks)
        top3 = scored[:3]

        for task in top3:
            task["suggestion_reason"] = task["explanation"]

        return JsonResponse(top3, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
