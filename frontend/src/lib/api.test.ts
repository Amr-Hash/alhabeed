import { unwrapList } from "@/lib/api";

describe("unwrapList", () => {
  it("returns array as-is", () => {
    expect(unwrapList([1, 2])).toEqual([1, 2]);
  });

  it("unwraps paginated results", () => {
    expect(unwrapList({ results: [1, 2] })).toEqual([1, 2]);
  });

  it("returns empty array for missing results", () => {
    expect(unwrapList({})).toEqual([]);
  });
});
