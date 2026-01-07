// range-serializer.js
import * as SelectorGenerator from './selector-generator.js';

export function serialize(range) {
  const start = SelectorGenerator.generate(range.startContainer);
  start.offset = range.startOffset;
  const end = SelectorGenerator.generate(range.endContainer);
  end.offset = range.endOffset;

  return {start:start, end:end};
}

export function deserialize(result) {
  try{
    const range = document.createRange();
    const startNode = SelectorGenerator.find(result.start);
    const endNode = SelectorGenerator.find(result.end);

    range.setStart(startNode, result.start.offset);
    range.setEnd(endNode, result.end.offset);

    return range;
  }
  catch{
    // console.log("deserialize(result) failed, return null, try it later!")
    return null
  }

  
  
}