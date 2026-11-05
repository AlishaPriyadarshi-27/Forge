"""
FORGE Visual Learning Engine
Animation Schema

Generic schema and validation layer for AI-generated visual lessons.

This file defines:
- VisualElement
- AnimationAction
- Narration
- AnimationScene
- AnimationLesson
- Lesson validation
- JSON conversion helpers

IMPORTANT:
This file must remain independent.
DO NOT import animation_schema from itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ============================================================
# VISUAL ELEMENT
# ============================================================

@dataclass
class VisualElement:
    """
    A generic visual object that can appear inside a scene.

    Examples:
    - array
    - node
    - edge
    - pointer
    - label
    - equation
    - table
    - code
    - graph
    - tree
    - database
    - server
    - client
    - matrix
    - flow
    """

    id: str
    type: str
    data: Any = None

    position: Dict[str, float] = field(
        default_factory=lambda: {
            "x": 0.0,
            "y": 0.0,
        }
    )

    style: Dict[str, Any] = field(default_factory=dict)

    label: str = ""


# ============================================================
# ANIMATION ACTION
# ============================================================

@dataclass
class AnimationAction:
    """
    Represents one visual transformation.

    Examples:
    create
    remove
    move
    highlight
    compare
    transform
    connect
    disconnect
    fade
    zoom
    pan
    replace
    reorder
    split
    merge
    trace
    update
    wait
    """

    action: str
    target: str

    value: Any = None

    duration: float = 0.8

    easing: str = "smooth"

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# NARRATION
# ============================================================

@dataclass
class Narration:
    """
    Voice-over information associated with a scene.
    """

    text: str

    start_after: float = 0.0

    duration: Optional[float] = None

    voice: Optional[str] = None

    language: str = "en"


# ============================================================
# ANIMATION SCENE
# ============================================================

@dataclass
class AnimationScene:
    """
    One complete teaching scene.

    A scene contains:
    - visual elements
    - animation actions
    - narration
    - camera information
    """

    id: str

    title: str

    purpose: str

    elements: List[VisualElement] = field(
        default_factory=list
    )

    actions: List[AnimationAction] = field(
        default_factory=list
    )

    narration: Narration = field(
        default_factory=lambda: Narration(
            text=""
        )
    )

    duration: float = 5.0

    camera: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# ANIMATION LESSON
# ============================================================

@dataclass
class AnimationLesson:
    """
    Complete generic FORGE visual lesson.

    This is topic-independent.

    The same structure can represent:
    - Binary Search
    - Linked Lists
    - Graph Algorithms
    - TCP/IP
    - SQL
    - Neural Networks
    - Machine Learning
    - Operating Systems
    - Cloud
    - Mathematics
    - etc.
    """

    topic: str

    title: str

    learning_objective: str

    difficulty: str

    language: str

    estimated_duration: float

    scenes: List[AnimationScene] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# BASIC HELPERS
# ============================================================

def _is_number(value: Any) -> bool:
    """
    Check whether a value is numeric.
    """

    return isinstance(
        value,
        (int, float)
    ) and not isinstance(
        value,
        bool
    )


# ============================================================
# VALIDATE VISUAL ELEMENT
# ============================================================

def validate_visual_element(
    element: Any,
    path: str = "element"
) -> List[str]:
    """
    Validate one visual element.

    Returns a list of validation errors.
    """

    errors: List[str] = []

    if not isinstance(element, dict):
        return [
            f"{path} must be an object."
        ]

    element_id = element.get("id")

    if not isinstance(element_id, str) or not element_id.strip():
        errors.append(
            f"{path}.id must be a non-empty string."
        )

    element_type = element.get("type")

    if not isinstance(element_type, str) or not element_type.strip():
        errors.append(
            f"{path}.type must be a non-empty string."
        )

    position = element.get("position")

    if position is not None:

        if not isinstance(position, dict):
            errors.append(
                f"{path}.position must be an object."
            )

        else:

            if "x" in position and not _is_number(position["x"]):
                errors.append(
                    f"{path}.position.x must be numeric."
                )

            if "y" in position and not _is_number(position["y"]):
                errors.append(
                    f"{path}.position.y must be numeric."
                )

    style = element.get("style")

    if style is not None and not isinstance(style, dict):
        errors.append(
            f"{path}.style must be an object."
        )

    return errors


# ============================================================
# VALIDATE ACTION
# ============================================================

def validate_animation_action(
    action: Any,
    path: str = "action"
) -> List[str]:
    """
    Validate one animation action.
    """

    errors: List[str] = []

    if not isinstance(action, dict):
        return [
            f"{path} must be an object."
        ]

    action_name = action.get("action")

    if not isinstance(action_name, str) or not action_name.strip():
        errors.append(
            f"{path}.action must be a non-empty string."
        )

    target = action.get("target")

    if not isinstance(target, str) or not target.strip():
        errors.append(
            f"{path}.target must be a non-empty string."
        )

    duration = action.get("duration")

    if duration is not None:

        if not _is_number(duration):
            errors.append(
                f"{path}.duration must be numeric."
            )

        elif duration < 0:
            errors.append(
                f"{path}.duration cannot be negative."
            )

    easing = action.get("easing")

    if easing is not None and not isinstance(easing, str):
        errors.append(
            f"{path}.easing must be a string."
        )

    metadata = action.get("metadata")

    if metadata is not None and not isinstance(metadata, dict):
        errors.append(
            f"{path}.metadata must be an object."
        )

    return errors


# ============================================================
# VALIDATE NARRATION
# ============================================================

def validate_narration(
    narration: Any,
    path: str = "narration"
) -> List[str]:
    """
    Validate narration.
    """

    errors: List[str] = []

    if not isinstance(narration, dict):
        return [
            f"{path} must be an object."
        ]

    text = narration.get("text")

    if not isinstance(text, str):
        errors.append(
            f"{path}.text must be a string."
        )

    start_after = narration.get("start_after")

    if start_after is not None and not _is_number(start_after):
        errors.append(
            f"{path}.start_after must be numeric."
        )

    duration = narration.get("duration")

    if duration is not None and not _is_number(duration):
        errors.append(
            f"{path}.duration must be numeric or null."
        )

    voice = narration.get("voice")

    if voice is not None and not isinstance(voice, str):
        errors.append(
            f"{path}.voice must be a string or null."
        )

    language = narration.get("language")

    if language is not None and not isinstance(language, str):
        errors.append(
            f"{path}.language must be a string."
        )

    return errors


# ============================================================
# VALIDATE SCENE
# ============================================================

def validate_animation_scene(
    scene: Any,
    path: str = "scene"
) -> List[str]:
    """
    Validate one complete animation scene.
    """

    errors: List[str] = []

    if not isinstance(scene, dict):
        return [
            f"{path} must be an object."
        ]

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    for field_name in [
        "id",
        "title",
        "purpose",
    ]:

        value = scene.get(field_name)

        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"{path}.{field_name} must be a non-empty string."
            )

    # --------------------------------------------------------
    # Elements
    # --------------------------------------------------------

    elements = scene.get("elements", [])

    if not isinstance(elements, list):
        errors.append(
            f"{path}.elements must be an array."
        )

    else:

        for index, element in enumerate(elements):

            errors.extend(
                validate_visual_element(
                    element,
                    f"{path}.elements[{index}]"
                )
            )

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------

    actions = scene.get("actions", [])

    if not isinstance(actions, list):
        errors.append(
            f"{path}.actions must be an array."
        )

    else:

        for index, action in enumerate(actions):

            errors.extend(
                validate_animation_action(
                    action,
                    f"{path}.actions[{index}]"
                )
            )

    # --------------------------------------------------------
    # Narration
    # --------------------------------------------------------

    if "narration" not in scene:

        errors.append(
            f"{path}.narration is required."
        )

    else:

        errors.extend(
            validate_narration(
                scene["narration"],
                f"{path}.narration"
            )
        )

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    duration = scene.get("duration")

    if duration is not None:

        if not _is_number(duration):
            errors.append(
                f"{path}.duration must be numeric."
            )

        elif duration <= 0:
            errors.append(
                f"{path}.duration must be greater than zero."
            )

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    camera = scene.get("camera")

    if camera is not None and not isinstance(camera, dict):
        errors.append(
            f"{path}.camera must be an object."
        )

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = scene.get("metadata")

    if metadata is not None and not isinstance(metadata, dict):
        errors.append(
            f"{path}.metadata must be an object."
        )

    return errors


# ============================================================
# VALIDATE COMPLETE LESSON
# ============================================================

def validate_lesson_dict(
    lesson: Any
) -> List[str]:
    """
    Validate the complete AI-generated lesson.

    IMPORTANT:
    This function intentionally returns errors instead of raising
    exceptions because AnimationPlanner handles the errors and
    generates a useful ValueError message.
    """

    errors: List[str] = []

    # --------------------------------------------------------
    # Root object
    # --------------------------------------------------------

    if not isinstance(lesson, dict):

        return [
            "lesson must be an object."
        ]

    # --------------------------------------------------------
    # Required root fields
    # --------------------------------------------------------

    required_string_fields = [
        "topic",
        "title",
        "learning_objective",
        "difficulty",
        "language",
    ]

    for field_name in required_string_fields:

        value = lesson.get(field_name)

        if not isinstance(value, str) or not value.strip():

            errors.append(
                f"{field_name} must be a non-empty string."
            )

    # --------------------------------------------------------
    # Estimated duration
    # --------------------------------------------------------

    estimated_duration = lesson.get(
        "estimated_duration"
    )

    if estimated_duration is None:

        errors.append(
            "estimated_duration is required."
        )

    elif not _is_number(estimated_duration):

        errors.append(
            "estimated_duration must be numeric."
        )

    elif estimated_duration <= 0:

        errors.append(
            "estimated_duration must be greater than zero."
        )

    # --------------------------------------------------------
    # Scenes
    # --------------------------------------------------------

    scenes = lesson.get("scenes")

    if not isinstance(scenes, list):

        errors.append(
            "scenes must be an array."
        )

        return errors

    if len(scenes) == 0:

        errors.append(
            "scenes must contain at least one scene."
        )

        return errors

    # --------------------------------------------------------
    # Scene validation
    # --------------------------------------------------------

    scene_ids = set()

    for index, scene in enumerate(scenes):

        path = f"scenes[{index}]"

        errors.extend(
            validate_animation_scene(
                scene,
                path
            )
        )

        if isinstance(scene, dict):

            scene_id = scene.get("id")

            if isinstance(scene_id, str):

                if scene_id in scene_ids:

                    errors.append(
                        f"{path}.id '{scene_id}' is duplicated."
                    )

                scene_ids.add(scene_id)

    # --------------------------------------------------------
    # Metadata
    # --------------------------------------------------------

    metadata = lesson.get("metadata")

    if metadata is not None and not isinstance(metadata, dict):

        errors.append(
            "metadata must be an object."
        )

    return errors


# ============================================================
# CONVERT LESSON TO DICTIONARY
# ============================================================

def lesson_to_dict(
    lesson: Any
) -> Dict[str, Any]:
    """
    Convert an AnimationLesson dataclass to a JSON-ready dict.

    Also accepts an already-existing dictionary.
    """

    if isinstance(lesson, dict):

        return lesson

    if isinstance(lesson, AnimationLesson):

        return asdict(lesson)

    raise TypeError(
        "lesson must be an AnimationLesson or dictionary."
    )


# ============================================================
# CONVERT DICTIONARY TO DATACLASSES
# ============================================================

def lesson_from_dict(
    data: Dict[str, Any]
) -> AnimationLesson:
    """
    Convert a validated dictionary into AnimationLesson
    dataclasses.
    """

    if not isinstance(data, dict):

        raise TypeError(
            "data must be a dictionary."
        )

    validation_errors = validate_lesson_dict(
        data
    )

    if validation_errors:

        raise ValueError(
            "Invalid animation lesson: "
            + "; ".join(validation_errors)
        )

    scenes: List[AnimationScene] = []

    for scene_data in data.get("scenes", []):

        elements = [
            VisualElement(
                id=element.get("id", ""),
                type=element.get("type", ""),
                data=element.get("data"),
                position=element.get(
                    "position",
                    {"x": 0.0, "y": 0.0}
                ),
                style=element.get(
                    "style",
                    {}
                ),
                label=element.get(
                    "label",
                    ""
                ),
            )
            for element in scene_data.get(
                "elements",
                []
            )
        ]

        actions = [
            AnimationAction(
                action=action.get(
                    "action",
                    ""
                ),
                target=action.get(
                    "target",
                    ""
                ),
                value=action.get(
                    "value"
                ),
                duration=action.get(
                    "duration",
                    0.8
                ),
                easing=action.get(
                    "easing",
                    "smooth"
                ),
                metadata=action.get(
                    "metadata",
                    {}
                ),
            )
            for action in scene_data.get(
                "actions",
                []
            )
        ]

        narration_data = scene_data.get(
            "narration",
            {}
        )

        narration = Narration(
            text=narration_data.get(
                "text",
                ""
            ),
            start_after=narration_data.get(
                "start_after",
                0
            ),
            duration=narration_data.get(
                "duration"
            ),
            voice=narration_data.get(
                "voice"
            ),
            language=narration_data.get(
                "language",
                data.get(
                    "language",
                    "en"
                )
            ),
        )

        scenes.append(
            AnimationScene(
                id=scene_data.get(
                    "id",
                    ""
                ),
                title=scene_data.get(
                    "title",
                    ""
                ),
                purpose=scene_data.get(
                    "purpose",
                    ""
                ),
                elements=elements,
                actions=actions,
                narration=narration,
                duration=scene_data.get(
                    "duration",
                    5
                ),
                camera=scene_data.get(
                    "camera",
                    {}
                ),
                metadata=scene_data.get(
                    "metadata",
                    {}
                ),
            )
        )

    return AnimationLesson(
        topic=data.get(
            "topic",
            ""
        ),
        title=data.get(
            "title",
            ""
        ),
        learning_objective=data.get(
            "learning_objective",
            ""
        ),
        difficulty=data.get(
            "difficulty",
            "intermediate"
        ),
        language=data.get(
            "language",
            "en"
        ),
        estimated_duration=data.get(
            "estimated_duration",
            30
        ),
        scenes=scenes,
        metadata=data.get(
            "metadata",
            {}
        ),
    )


# ============================================================
# SIMPLE VALIDATION HELPER
# ============================================================

def validate_lesson(
    lesson: Any
) -> bool:
    """
    Return True when the lesson is valid.
    """

    return len(
        validate_lesson_dict(lesson)
    ) == 0


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "VisualElement",
    "AnimationAction",
    "Narration",
    "AnimationScene",
    "AnimationLesson",
    "validate_visual_element",
    "validate_animation_action",
    "validate_narration",
    "validate_animation_scene",
    "validate_lesson_dict",
    "validate_lesson",
    "lesson_to_dict",
    "lesson_from_dict",
]