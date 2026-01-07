// selector-generator.js - ES Module 版本

function childNodeIndexOf(parentNode, childNode) {
  const childNodes = parentNode.childNodes;
  for (let i = 0, l = childNodes.length; i < l; i++) {
    if (childNodes[i] === childNode) return i;
  }
  return -1; // 如果没找到返回-1
}

function computedNthIndex(childElement) {
  const childNodes = childElement.parentNode.childNodes;
  const tagName = childElement.tagName;
  let elementsWithSameTag = 0;

  for (let i = 0, l = childNodes.length; i < l; i++) {
    if (childNodes[i] === childElement) return elementsWithSameTag + 1;
    if (childNodes[i].tagName === tagName) elementsWithSameTag++;
  }
  return 0;
}

export function generate(node) {
  const textNodeIndex = childNodeIndexOf(node.parentNode, node);
  let currentNode = node;
  const tagNames = [];

  while (currentNode) {
    const tagName = currentNode.tagName;

    if (tagName) {
      const nthIndex = computedNthIndex(currentNode);
      let selector = tagName;

      if (nthIndex > 1) {
        selector += `:nth-of-type(${nthIndex})`;
      }

      tagNames.push(selector);
    }

    currentNode = currentNode.parentNode;
  }

  return {
    selector: tagNames.reverse().join(" > ").toLowerCase(),
    childNodeIndex: textNodeIndex
  };
}

export function find(result) {
  const element = document.querySelector(result.selector);
  if (!element) {
    throw new Error(`Unable to find element with selector: ${result.selector}`);
  }
  return element.childNodes[result.childNodeIndex];
}

// 默认导出
export default {
  generate,
  find
};