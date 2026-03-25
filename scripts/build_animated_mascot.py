from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path('/Users/marcelofinamorvieira/sillyProjects')
SRC = ROOT / 'assets' / 'mascot-source.svg'
OUT = ROOT / 'assets' / 'mascot.svg'
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)


def tag(name: str) -> str:
    return f'{{{SVG_NS}}}{name}'


def clone(children: list[ET.Element], index: int) -> ET.Element:
    return deepcopy(children[index - 1])


def clone_many(children: list[ET.Element], indices: list[int]) -> list[ET.Element]:
    return [clone(children, index) for index in indices]


def group(group_id: str, items: list[ET.Element], attrs: dict[str, str] | None = None) -> ET.Element:
    node = ET.Element(tag('g'), {'id': group_id})
    if attrs:
        node.attrib.update(attrs)
    for item in items:
        node.append(item)
    return node


source_root = ET.parse(SRC).getroot()
source_children = list(source_root)

new_root = ET.Element(
    tag('svg'),
    {
        'version': source_root.attrib.get('version', '1.1'),
        'viewBox': source_root.attrib.get('viewBox', '0 0 1008 1210'),
        'role': 'img',
        'aria-labelledby': 'mascotTitle mascotDesc',
    },
)

ET.SubElement(new_root, tag('title'), {'id': 'mascotTitle'}).text = 'Animated Dato mascot'
ET.SubElement(new_root, tag('desc'), {'id': 'mascotDesc'}).text = (
    'Structured mascot asset prepared for lightweight motion inside the Chrome extension.'
)

style = ET.SubElement(new_root, tag('style'))
style.text = '''
  #mascot-root,
  #arm-left,
  #arm-right,
  #leg-left,
  #leg-right,
  #eye-left-rig,
  #eye-right-rig,
  #pupil-left,
  #pupil-right,
  #mouth-neutral,
  #mouth-talk-a,
  #mouth-talk-b {
    transform-box: fill-box;
  }

  #mascot-root {
    transform-origin: 504px 800px;
    animation: mascot-intro 920ms ease-out 1 both, mascot-idle 5.2s ease-in-out 1.1s infinite;
  }

  #arm-right {
    transform-origin: 793px 522px;
    animation: arm-right-intro 1.15s ease-out 1 both, arm-right-idle 6.0s ease-in-out 1.5s infinite;
  }

  #arm-left {
    transform-origin: 202px 530px;
    animation: arm-left-idle 6.4s ease-in-out 1.7s infinite;
  }

  #leg-right {
    transform-origin: 550px 792px;
    animation: leg-right-idle 4.8s ease-in-out 1.2s infinite;
  }

  #leg-left {
    transform-origin: 454px 798px;
    animation: leg-left-idle 4.8s ease-in-out 1.2s infinite reverse;
  }

  #eye-left-rig {
    transform-origin: 419px 265px;
    animation: eye-intro 1.08s linear 1 both, eye-idle 6.9s step-end 2.0s infinite;
  }

  #eye-right-rig {
    transform-origin: 610px 262px;
    animation: eye-intro 1.08s linear 1 both, eye-idle 6.9s step-end 2.15s infinite;
  }

  #pupil-left {
    transform-origin: 422px 280px;
    animation: pupil-drift-left 4.4s ease-in-out 1.4s infinite alternate;
  }

  #pupil-right {
    transform-origin: 605px 274px;
    animation: pupil-drift-right 4.1s ease-in-out 1.5s infinite alternate;
  }

  #mouth-neutral,
  #mouth-talk-a,
  #mouth-talk-b {
    transform-origin: 505px 498px;
  }

  #mouth-neutral {
    animation: mouth-neutral-intro 1.05s step-end 1 both;
  }

  #mouth-talk-a {
    opacity: 0;
    animation: mouth-talk-a 1.05s step-end 1 both;
  }

  #mouth-talk-b {
    opacity: 0;
    animation: mouth-talk-b 1.05s step-end 1 both;
  }

  @keyframes mascot-intro {
    0% { transform: translateY(18px) scale(0.985); }
    48% { transform: translateY(-8px) scale(1.01); }
    100% { transform: translateY(0) scale(1); }
  }

  @keyframes mascot-idle {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-9px); }
  }

  @keyframes arm-right-intro {
    0% { transform: rotate(0deg); }
    22% { transform: rotate(-14deg); }
    42% { transform: rotate(18deg); }
    62% { transform: rotate(4deg); }
    82% { transform: rotate(15deg); }
    100% { transform: rotate(6deg); }
  }

  @keyframes arm-right-idle {
    0%, 100% { transform: rotate(6deg); }
    50% { transform: rotate(10deg); }
  }

  @keyframes arm-left-idle {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(-4deg); }
  }

  @keyframes leg-right-idle {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(2.2deg); }
  }

  @keyframes leg-left-idle {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(1.8deg); }
  }

  @keyframes eye-intro {
    0%, 24%, 58%, 100% { transform: scaleY(1); }
    31%, 39% { transform: scaleY(0.08); }
  }

  @keyframes eye-idle {
    0%, 91%, 100% { transform: scaleY(1); }
    94%, 97% { transform: scaleY(0.08); }
  }

  @keyframes pupil-drift-left {
    0% { transform: translate(0, 0); }
    40% { transform: translate(3px, -1px); }
    100% { transform: translate(-3px, 1px); }
  }

  @keyframes pupil-drift-right {
    0% { transform: translate(0, 0); }
    35% { transform: translate(-3px, 0); }
    100% { transform: translate(3px, 1px); }
  }

  @keyframes mouth-neutral-intro {
    0%, 15% { opacity: 1; }
    18%, 34% { opacity: 0; }
    36%, 46% { opacity: 1; }
    49%, 66% { opacity: 0; }
    70%, 100% { opacity: 1; }
  }

  @keyframes mouth-talk-a {
    0%, 17%, 36%, 100% { opacity: 0; }
    19%, 32% { opacity: 1; }
  }

  @keyframes mouth-talk-b {
    0%, 47%, 67%, 100% { opacity: 0; }
    50%, 63% { opacity: 1; }
  }

  @media (prefers-reduced-motion: reduce) {
    #mascot-root,
    #arm-left,
    #arm-right,
    #leg-left,
    #leg-right,
    #eye-left-rig,
    #eye-right-rig,
    #pupil-left,
    #pupil-right,
    #mouth-neutral,
    #mouth-talk-a,
    #mouth-talk-b {
      animation: none !important;
      transform: none !important;
    }

    #mouth-neutral {
      opacity: 1 !important;
    }

    #mouth-talk-a,
    #mouth-talk-b {
      opacity: 0 !important;
    }
  }
'''

leg_left = group(
    'leg-left',
    clone_many(source_children, [34, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48, 50, 51, 53, 54]),
)
leg_right = group(
    'leg-right',
    clone_many(source_children, [32, 33, 35, 36, 43, 44, 49, 52]),
)
arm_left = group('arm-left', clone_many(source_children, [21, 22, 29, 31]))
arm_right = group('arm-right', clone_many(source_children, [19, 20, 27, 28, 30]))
body_shell = group('body-shell', clone_many(source_children, [1, 3, 5, 26]))
face_static = group('face-static', clone_many(source_children, [2, 6, 7, 12, 13, 14, 16]))

eye_left = ET.Element(tag('g'), {'id': 'eye-left-rig'})
eye_left.append(clone(source_children, 8))
pupil_left_wrap = ET.SubElement(eye_left, tag('g'), {'id': 'pupil-left'})
pupil_left_wrap.append(clone(source_children, 11))

eye_right = ET.Element(tag('g'), {'id': 'eye-right-rig'})
eye_right.append(clone(source_children, 9))
pupil_right_wrap = ET.SubElement(eye_right, tag('g'), {'id': 'pupil-right'})
pupil_right_wrap.append(clone(source_children, 10))

mouth_indices = [4, 15, 17, 18, 23, 24]
mouth_rig = ET.Element(tag('g'), {'id': 'mouth-rig'})
mouth_neutral = group('mouth-neutral', clone_many(source_children, mouth_indices))
mouth_talk_a = group(
    'mouth-talk-a',
    clone_many(source_children, mouth_indices),
    {'transform': 'translate(505 498) scale(1.03 1.08) translate(-505 -498)'},
)
mouth_talk_b = group(
    'mouth-talk-b',
    clone_many(source_children, mouth_indices),
    {'transform': 'translate(505 498) scale(0.98 0.92) translate(-505 -498)'},
)
mouth_rig.extend([mouth_neutral, mouth_talk_a, mouth_talk_b])

mascot_root = ET.SubElement(new_root, tag('g'), {'id': 'mascot-root'})
mascot_root.extend([
    leg_left,
    leg_right,
    arm_left,
    arm_right,
    body_shell,
    face_static,
    eye_left,
    eye_right,
    mouth_rig,
])

ET.indent(ET.ElementTree(new_root), space='  ')
ET.ElementTree(new_root).write(OUT, encoding='utf-8', xml_declaration=True)
print(f'Wrote {OUT}')
