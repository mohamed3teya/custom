"use strict";
/*
 *coursesDetailsLoad()
 *render courses to #CoursesDetailsTable div
 *params event  id current target checked from checkbox
 */
function _coursesDetailsLoad(event) {
  const CoursesDetailsTableDom = document.querySelector("#CoursesDetailsTable");

  const coursesDetailsTable = `
  <table class="table table-condensed text-center">
  <!-- CoursesDetailsTable thead -->
  <thead>
    <tr id="CoursesDetailsTr">
      <th><i  class="fa fa-check-square-o" aria-hidden="true" ></i> check </th>
      <th><i class="fa fa-pie-chart" aria-hidden="true"></i>Available</th>
      <th><i class="fa fa-calendar" aria-hidden="true"></i>Day</th>
      <th><i class="fa fa-clock-o" aria-hidden="true"></i>From Time</th>
      <th><i class="fa fa-clock-o" aria-hidden="true"></i>To Time</th>
      <th><i class="fa fa-tags" aria-hidden="true"></i>Type</th>
      <th><i class="fa fa-users" aria-hidden="true"></i>Group</th>
      <th><i class="fa fa-map-marker" aria-hidden="true"></i>Facility</th>
      <th><i class="fa fa-address-card" aria-hidden="true" ></i>Instructor</th>
      <th><i class="fa fa-certificate" aria-hidden="true"></i>Status</th>
    </tr>
  </thead>
  <!-- /.CoursesDetailsTable thead -->

  <!-- CoursesDetailsTable tbody -->
     <tbody id="CoursesData"></tbody>
  <!-- /.CoursesDetailsTable tbody -->
</table>
  `;

  CoursesDetailsTableDom.innerHTML = coursesDetailsTable;

  //Selectors
  let SessionsTbodyDom = document.querySelector("#CoursesData");
  let CoursesDetailsTrDom = document.querySelector("#CoursesDetailsTr");

  let subID = event.currentTarget.id; // currentTarget id checked ex. subject-1
  let subIDFind = subID.split("-"); // currentTarget split    ex. [subject] [1]

  let SessionsFind = mainOBJ.find((item) => {
    return item.idSubject == subIDFind[1];
  });

  let CoursesData = SessionsFind.Sessions; // all Sessions here

  // if no results on Sessions
  if (CoursesData.length == 0) {
    CoursesDetailsTrDom.style.display = "none";
    return (SessionsTbodyDom.innerHTML = `
    <td colspan="10">
      <div class="callout callout-info">
        <h5>No Sessions Available , Please Select Course Subject .</h5>
     </div>`);
  } else {
    CoursesDetailsTrDom.style.display = "table-row";
  }

  let SessionsResponse = CoursesData.map((SessionsItem) => {
    let {
      sessionId,
      Available,
      Facility,
      FromTime,
      Group,
      Instructor,
      Status,
      day,
      toTime,
      type,
    } = SessionsItem;

   
    let CheckedStatus;
    //find it in localstorage if checked  or not 
    let ArrayChecked = JSON.parse(window.localStorage["courseSelections"]); // localstorage array

    //split ex.subject-1-sessions-2 to git id (subject && sessions ) chosen 
    let currentElementId = `subject-${subIDFind[1]}-sessions-${sessionId}`;

    //map array localstorage
    ArrayChecked.find((element) => {
      // save checked value if found
      if (element == currentElementId) {
        return (CheckedStatus = "checked");
      }
    });

    return `<tr data-course="${currentElementId}">
              <td><input id="${currentElementId}" type="checkbox"  ${CheckedStatus}   class="SessionsChoices" /></label></label></td>
              <td>${Available}</td>
              <td><span>${day}</span></td>
              <td><span>${FromTime}</span></td>
              <td><span>${toTime}</span ></td>
              <td><span>${type}</span></td>
              <td><span>${Group}</span></td>
              <td><span>${Facility}</span></td>
              <td> 
              <span>
            ${Instructor.map((name) => {
              return `<p class="Instructor"><span>${name}</span></p>`;
            }).join("")} 
          </span>
        </td>
        <td><span class="text-green">${Status}</span></td>
         
      </tr>
      `;
  }).join("");

  SessionsTbodyDom.innerHTML = SessionsResponse;

  // recall  iCheck to SessionsChoices
  $('input[type="checkbox"].SessionsChoices').iCheck({
    checkboxClass: "icheckbox_flat-yellow",
    radioClass: "iradio_flat-yellow",
  });
}